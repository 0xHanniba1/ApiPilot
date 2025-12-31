from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.test_case import TestCase, Assertion, Extractor
from app.models.environment import Environment, EnvVariable
from app.models.execution import TestExecution, ExecutionDetail
from app.engine import TestExecutor, ExecutionResult
from app.core.exceptions import NotFoundError


class ExecutionService:
    """执行服务"""

    def __init__(self):
        self.executor = TestExecutor()

    async def execute_case(
        self,
        db: AsyncSession,
        case_id: int,
        environment_id: int,
        trigger_type: str = "manual",
    ) -> tuple[TestExecution, ExecutionDetail]:
        """
        执行单个用例并保存记录

        Args:
            db: 数据库会话
            case_id: 用例 ID
            environment_id: 环境 ID
            trigger_type: 触发类型 (manual/schedule/api)

        Returns:
            (TestExecution, ExecutionDetail) 元组
        """
        # 1. 获取用例信息
        test_case = await self._get_test_case(db, case_id)
        if not test_case:
            raise NotFoundError(f"用例不存在: {case_id}")

        # 2. 获取环境信息
        environment = await self._get_environment(db, environment_id)
        if not environment:
            raise NotFoundError(f"环境不存在: {environment_id}")

        # 3. 构建环境变量字典
        env_vars = {var.key: var.value for var in environment.variables}

        # 4. 构建用例配置
        case_config = self._build_case_config(test_case)

        # 5. 创建执行记录
        started_at = datetime.now()
        execution = TestExecution(
            test_case_id=case_id,
            environment_id=environment_id,
            trigger_type=trigger_type,
            status="running",
            total_count=1,
            passed_count=0,
            failed_count=0,
            skipped_count=0,
            started_at=started_at,
        )
        db.add(execution)
        await db.flush()

        # 6. 执行用例
        exec_result = await self.executor.execute(
            base_url=environment.base_url,
            test_case=case_config,
            env_vars=env_vars,
        )

        finished_at = datetime.now()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)

        # 7. 创建执行详情
        detail = ExecutionDetail(
            execution_id=execution.id,
            test_case_id=case_id,
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
            executed_at=finished_at,
        )
        db.add(detail)

        # 8. 更新执行记录状态
        execution.status = exec_result.status
        execution.duration_ms = duration_ms
        execution.finished_at = finished_at

        if exec_result.status == "passed":
            execution.passed_count = 1
        elif exec_result.status == "failed":
            execution.failed_count = 1
        else:  # error
            execution.failed_count = 1

        await db.commit()
        await db.refresh(execution)
        await db.refresh(detail)

        return execution, detail

    async def debug_execute(
        self,
        db: AsyncSession,
        environment_id: int,
        method: str,
        path: str,
        headers: dict = None,
        params: dict = None,
        body_type: str = "none",
        body_content: str = None,
        assertions: list = None,
        extractors: list = None,
    ) -> ExecutionResult:
        """
        调试执行（不保存记录）

        Args:
            db: 数据库会话
            environment_id: 环境 ID
            method: 请求方法
            path: 请求路径
            headers: 请求头
            params: Query 参数
            body_type: Body 类型
            body_content: Body 内容
            assertions: 断言配置列表
            extractors: 提取器配置列表

        Returns:
            ExecutionResult 对象
        """
        # 获取环境信息
        environment = await self._get_environment(db, environment_id)
        if not environment:
            raise NotFoundError(f"环境不存在: {environment_id}")

        # 构建环境变量字典
        env_vars = {var.key: var.value for var in environment.variables}

        # 构建用例配置
        case_config = {
            "method": method,
            "path": path,
            "headers": headers or {},
            "params": params or {},
            "body_type": body_type,
            "body_content": body_content,
            "assertions": assertions or [],
            "extractors": extractors or [],
        }

        # 执行用例
        return await self.executor.execute(
            base_url=environment.base_url,
            test_case=case_config,
            env_vars=env_vars,
        )

    async def _get_test_case(self, db: AsyncSession, case_id: int) -> TestCase | None:
        """获取用例（包含断言和提取器）"""
        stmt = (
            select(TestCase)
            .where(TestCase.id == case_id)
            .options(
                selectinload(TestCase.assertions),
                selectinload(TestCase.extractors),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_environment(self, db: AsyncSession, environment_id: int) -> Environment | None:
        """获取环境（包含环境变量）"""
        stmt = (
            select(Environment)
            .where(Environment.id == environment_id)
            .options(selectinload(Environment.variables))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def _build_case_config(self, test_case: TestCase) -> dict:
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


# 单例
execution_service = ExecutionService()
