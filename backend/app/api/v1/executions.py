from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success, ResponseModel
from app.schemas.execution import (
    ExecuteCaseRequest,
    DebugExecuteRequest,
    DebugResponse,
    ExecutionDetailResponse,
)
from app.services.execution_service import execution_service

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
