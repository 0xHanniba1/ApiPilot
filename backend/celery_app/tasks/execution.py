import asyncio
from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import select, create_engine
from sqlalchemy.orm import selectinload, Session, sessionmaker

from app.config import settings
from app.models.test_suite import TestSuite, SuiteCase
from app.models.environment import Environment, EnvVariable
from app.models.execution import TestExecution, ExecutionDetail
from app.engine import TestExecutor

logger = get_task_logger(__name__)

# 创建同步数据库引擎（用于 Celery）
sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2")
sync_engine = create_engine(sync_database_url, pool_pre_ping=True)
SyncSession = sessionmaker(bind=sync_engine)


def run_async(coro):
    """在同步环境中运行异步代码"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True, name="celery_app.tasks.execution.execute_suite_task")
def execute_suite_task(self, execution_id: int):
    """
    异步执行测试集任务
    
    Args:
        execution_id: 执行记录 ID
    """
    logger.info(f"开始执行测试集，execution_id={execution_id}")
    
    try:
        result = _execute_suite_sync(execution_id)
        logger.info(f"测试集执行完成，execution_id={execution_id}, result={result}")
        return result
    except Exception as e:
        logger.error(f"测试集执行失败，execution_id={execution_id}, error={str(e)}")
        # 更新执行状态为 error
        _update_execution_error(execution_id, str(e))
        raise


def _execute_suite_sync(execution_id: int) -> dict:
    """同步执行测试集（Celery worker 中调用）"""
    with SyncSession() as db:
        # 1. 获取执行记录
        execution = db.get(TestExecution, execution_id)
        if not execution:
            raise ValueError(f"执行记录不存在: {execution_id}")
        
        # 2. 获取测试集（包含用例）
        stmt = (
            select(TestSuite)
            .where(TestSuite.id == execution.suite_id)
            .options(
                selectinload(TestSuite.suite_cases).selectinload(SuiteCase.test_case)
            )
        )
        suite = db.execute(stmt).scalar_one_or_none()
        
        if not suite:
            raise ValueError(f"测试集不存在: {execution.suite_id}")
        
        # 3. 获取环境（包含变量）
        stmt = (
            select(Environment)
            .where(Environment.id == execution.environment_id)
            .options(selectinload(Environment.variables))
        )
        environment = db.execute(stmt).scalar_one_or_none()
        
        if not environment:
            raise ValueError(f"环境不存在: {execution.environment_id}")
        
        # 4. 构建环境变量
        env_vars = {var.key: var.value for var in environment.variables}
        extracted_vars = {}  # 用于用例间变量传递
        
        # 5. 更新执行状态为 running
        execution.status = "running"
        execution.started_at = datetime.now()
        execution.total_count = len(suite.suite_cases)
        db.commit()
        
        # 6. 按顺序排列用例
        sorted_cases = sorted(suite.suite_cases, key=lambda x: x.sort_order)
        
        # 7. 执行用例（使用异步执行器）
        executor = TestExecutor()
        passed_count = 0
        failed_count = 0
        
        if suite.execution_mode == "parallel":
            # 并行执行
            results = run_async(_execute_parallel(
                executor, environment.base_url, sorted_cases, env_vars
            ))
            for sc, exec_result in results:
                _save_execution_detail_sync(
                    db, execution.id, sc.test_case_id, exec_result
                )
                if exec_result.status == "passed":
                    passed_count += 1
                else:
                    failed_count += 1
        else:
            # 顺序执行
            for sc in sorted_cases:
                test_case = sc.test_case
                case_config = _build_case_config(test_case)
                
                exec_result = run_async(executor.execute(
                    base_url=environment.base_url,
                    test_case=case_config,
                    env_vars=env_vars,
                    extracted_vars=extracted_vars,
                ))
                
                # 保存执行详情
                _save_execution_detail_sync(
                    db, execution.id, test_case.id, exec_result
                )
                
                if exec_result.status == "passed":
                    passed_count += 1
                else:
                    failed_count += 1
                
                # 更新提取的变量
                if exec_result.extractor_results:
                    extracted_vars.update(exec_result.extractor_results)
        
        # 8. 更新执行记录
        execution.finished_at = datetime.now()
        execution.duration_ms = int(
            (execution.finished_at - execution.started_at).total_seconds() * 1000
        )
        execution.passed_count = passed_count
        execution.failed_count = failed_count
        execution.status = "passed" if failed_count == 0 else "failed"
        
        db.commit()
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "total_count": execution.total_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "duration_ms": execution.duration_ms,
        }


async def _execute_parallel(executor, base_url, suite_cases, env_vars):
    """并行执行用例"""
    import asyncio
    
    tasks = []
    for sc in suite_cases:
        test_case = sc.test_case
        case_config = _build_case_config(test_case)
        task = executor.execute(
            base_url=base_url,
            test_case=case_config,
            env_vars=env_vars,
        )
        tasks.append((sc, task))
    
    results = []
    for sc, task in tasks:
        exec_result = await task
        results.append((sc, exec_result))
    
    return results


def _save_execution_detail_sync(db: Session, execution_id, test_case_id, exec_result):
    """保存执行详情（同步）"""
    detail = ExecutionDetail(
        execution_id=execution_id,
        test_case_id=test_case_id,
        status=exec_result.status,
        request_url=exec_result.request_url,
        request_method=exec_result.request_method,
        request_headers=exec_result.request_headers,
        request_body=exec_result.request_body,
        response_status_code=exec_result.response_status_code,
        response_headers=exec_result.response_headers,
        response_body=exec_result.response_body,
        duration_ms=exec_result.duration_ms,
        assertion_results=exec_result.assertion_results,
        extractor_results=exec_result.extractor_results,
        error_message=exec_result.error_message,
        executed_at=datetime.now(),
    )
    db.add(detail)
    db.flush()
    return detail


def _build_case_config(test_case) -> dict:
    """构建用例配置"""
    return {
        "method": test_case.method,
        "path": test_case.path,
        "headers": test_case.headers or {},
        "params": test_case.params or {},
        "body_type": test_case.body_type,
        "body_content": test_case.body_content,
        "timeout": test_case.timeout,
        "assertions": [
            {
                "name": a.name,
                "type": a.type,
                "expression": a.expression,
                "operator": a.operator,
                "expected_value": a.expected_value,
            }
            for a in sorted(test_case.assertions, key=lambda x: x.sort_order)
        ],
        "extractors": [
            {
                "source": e.source,
                "expression": e.expression,
                "variable_name": e.variable_name,
                "default_value": e.default_value,
            }
            for e in sorted(test_case.extractors, key=lambda x: x.sort_order)
        ],
    }


def _update_execution_error(execution_id: int, error_message: str):
    """更新执行状态为错误"""
    with SyncSession() as db:
        execution = db.get(TestExecution, execution_id)
        if execution:
            execution.status = "error"
            execution.finished_at = datetime.now()
            if execution.started_at:
                execution.duration_ms = int(
                    (execution.finished_at - execution.started_at).total_seconds() * 1000
                )
            db.commit()
