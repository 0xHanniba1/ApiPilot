from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.response import success, paginate, ResponseModel, PaginationResponse
from app.core.exceptions import NotFoundError
from app.schemas.execution import (
    ExecuteCaseRequest,
    ExecuteSuiteRequest,
    DebugExecuteRequest,
    DebugResponse,
    ExecutionDetailResponse,
    TestExecutionResponse,
    TestExecutionListResponse,
    TestExecutionDetailResponse,
)
from app.services.execution_service import execution_service
from app.models.test_suite import TestSuite
from app.models.environment import Environment
from app.models.execution import TestExecution, ExecutionDetail

router = APIRouter(prefix="/execute", tags=["执行"])


@router.post("/case", response_model=ResponseModel)
async def execute_case(
    request: ExecuteCaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    执行单个用例

    同步执行，返回执行结果并保存记录
    """
    execution, detail = await execution_service.execute_case(
        db=db,
        case_id=request.test_case_id,
        environment_id=request.environment_id,
        trigger_type="manual",
    )

    # 构建响应
    response_data = {
        "execution_id": execution.id,
        "test_case_id": detail.test_case_id,
        "status": detail.status,
        "request_url": detail.request_url,
        "request_method": detail.request_method,
        "request_headers": detail.request_headers,
        "request_body": detail.request_body,
        "response_status_code": detail.response_status_code,
        "response_headers": detail.response_headers,
        "response_body": detail.response_body,
        "duration_ms": detail.duration_ms,
        "assertion_results": detail.assertion_results or [],
        "extractor_results": detail.extractor_results or {},
        "error_message": detail.error_message or "",
        "executed_at": detail.executed_at.isoformat() if detail.executed_at else None,
    }

    return success(data=response_data)


@router.post("/debug", response_model=ResponseModel)
async def debug_execute(
    request: DebugExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    调试执行

    用于用例编辑页的"发送请求"按钮，不保存执行记录
    """
    # 转换断言配置
    assertions = [
        {
            "name": a.name,
            "type": a.type,
            "expression": a.expression,
            "operator": a.operator,
            "expected_value": a.expected_value,
        }
        for a in request.assertions
    ]

    # 转换提取器配置
    extractors = [
        {
            "source": e.source,
            "expression": e.expression,
            "variable_name": e.variable_name,
            "default_value": e.default_value,
        }
        for e in request.extractors
    ]

    result = await execution_service.debug_execute(
        db=db,
        environment_id=request.environment_id,
        method=request.method,
        path=request.path,
        headers=request.headers,
        params=request.params,
        body_type=request.body_type,
        body_content=request.body_content,
        assertions=assertions,
        extractors=extractors,
    )

    # 构建响应
    response_data = DebugResponse(
        status=result.status,
        request_url=result.request_url,
        request_method=result.request_method,
        request_headers=result.request_headers,
        request_body=result.request_body,
        response_status_code=result.response_status_code,
        response_headers=result.response_headers,
        response_body=result.response_body,
        duration_ms=result.duration_ms,
        assertion_results=result.assertion_results,
        extractor_results=result.extractor_results,
        error_message=result.error_message,
    )

    return success(data=response_data.model_dump())


@router.post("/suite", response_model=ResponseModel)
async def execute_suite(
    request: ExecuteSuiteRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    异步执行测试集

    调用 Celery 任务异步执行，立即返回 execution_id
    客户端可通过 GET /executions/{id} 轮询执行状态
    """
    # 验证测试集存在
    suite = await db.get(TestSuite, request.suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {request.suite_id}")

    # 验证环境存在
    environment = await db.get(Environment, request.environment_id)
    if not environment:
        raise NotFoundError(f"环境不存在: {request.environment_id}")

    # 获取测试集用例数量
    from app.models.test_suite import SuiteCase
    from sqlalchemy import func

    count_stmt = select(func.count(SuiteCase.id)).where(
        SuiteCase.suite_id == request.suite_id
    )
    total_count = await db.scalar(count_stmt)

    # 创建执行记录
    execution = TestExecution(
        suite_id=request.suite_id,
        environment_id=request.environment_id,
        trigger_type="manual",
        status="pending",
        total_count=total_count,
        passed_count=0,
        failed_count=0,
        skipped_count=0,
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # 调用 Celery 任务
    from celery_app.tasks.execution import execute_suite_task
    execute_suite_task.delay(execution.id)

    return success(data={
        "execution_id": execution.id,
        "suite_id": request.suite_id,
        "environment_id": request.environment_id,
        "status": execution.status,
        "total_count": total_count,
        "message": "测试集执行任务已提交",
    })


@router.get("/executions", response_model=PaginationResponse)
async def list_executions(
    project_id: int = Query(None, description="项目ID"),
    suite_id: int = Query(None, description="测试集ID"),
    status: str = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取执行记录列表"""
    from sqlalchemy import func

    stmt = select(TestExecution)
    count_stmt = select(func.count(TestExecution.id))

    # 通过测试集关联项目筛选
    if project_id:
        stmt = stmt.join(TestSuite, TestExecution.suite_id == TestSuite.id).where(
            TestSuite.project_id == project_id
        )
        count_stmt = count_stmt.join(TestSuite, TestExecution.suite_id == TestSuite.id).where(
            TestSuite.project_id == project_id
        )

    if suite_id:
        stmt = stmt.where(TestExecution.suite_id == suite_id)
        count_stmt = count_stmt.where(TestExecution.suite_id == suite_id)

    if status:
        stmt = stmt.where(TestExecution.status == status)
        count_stmt = count_stmt.where(TestExecution.status == status)

    stmt = stmt.order_by(TestExecution.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    executions = result.scalars().all()

    total = await db.scalar(count_stmt)

    items = [
        {
            "id": e.id,
            "suite_id": e.suite_id,
            "test_case_id": e.test_case_id,
            "environment_id": e.environment_id,
            "trigger_type": e.trigger_type,
            "status": e.status,
            "total_count": e.total_count,
            "passed_count": e.passed_count,
            "failed_count": e.failed_count,
            "duration_ms": e.duration_ms,
            "started_at": e.started_at,
            "finished_at": e.finished_at,
        }
        for e in executions
    ]

    return paginate(items=items, total=total, page=page, page_size=page_size)


@router.get("/executions/{execution_id}", response_model=ResponseModel)
async def get_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取执行详情（用于轮询执行状态）"""
    stmt = (
        select(TestExecution)
        .where(TestExecution.id == execution_id)
        .options(selectinload(TestExecution.details))
    )
    result = await db.execute(stmt)
    execution = result.scalar_one_or_none()

    if not execution:
        raise NotFoundError(f"执行记录不存在: {execution_id}")

    details = [
        {
            "id": d.id,
            "execution_id": d.execution_id,
            "test_case_id": d.test_case_id,
            "status": d.status,
            "request_url": d.request_url,
            "request_method": d.request_method,
            "request_headers": d.request_headers,
            "request_body": d.request_body,
            "response_status_code": d.response_status_code,
            "response_headers": d.response_headers,
            "response_body": d.response_body,
            "duration_ms": d.duration_ms,
            "assertion_results": d.assertion_results,
            "extractor_results": d.extractor_results,
            "error_message": d.error_message,
            "executed_at": d.executed_at,
        }
        for d in sorted(execution.details, key=lambda x: x.id)
    ]

    return success(data={
        "id": execution.id,
        "suite_id": execution.suite_id,
        "test_case_id": execution.test_case_id,
        "environment_id": execution.environment_id,
        "trigger_type": execution.trigger_type,
        "status": execution.status,
        "total_count": execution.total_count,
        "passed_count": execution.passed_count,
        "failed_count": execution.failed_count,
        "skipped_count": execution.skipped_count,
        "duration_ms": execution.duration_ms,
        "started_at": execution.started_at,
        "finished_at": execution.finished_at,
        "created_at": execution.created_at,
        "details": details,
    })
