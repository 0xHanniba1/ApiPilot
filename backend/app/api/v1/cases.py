from fastapi import APIRouter, Query

from app.api.deps import DBSession
from app.services import case_service
from app.schemas import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    TestCaseListResponse, TestCaseDetailResponse,
    AssertionCreate, AssertionUpdate, AssertionResponse,
    ExtractorCreate, ExtractorUpdate, ExtractorResponse,
)
from app.core.response import success, paginate

router = APIRouter(tags=["用例管理"])


# ============ Test Case ============

@router.get("/modules/{module_id}/cases")
async def get_cases(
    db: DBSession,
    module_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """获取模块下的用例列表"""
    items, total = await case_service.get_cases(db, module_id, page, page_size)
    return paginate(
        items=[TestCaseListResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/modules/{module_id}/cases")
async def create_case(db: DBSession, module_id: int, data: TestCaseCreate):
    """创建用例"""
    case = await case_service.create_case(db, module_id, data)
    return success(data=TestCaseResponse.model_validate(case))


@router.get("/cases/{case_id}")
async def get_case(db: DBSession, case_id: int):
    """获取用例详情（包含断言、提取器）"""
    case = await case_service.get_case_by_id(db, case_id, with_details=True)
    return success(data=TestCaseDetailResponse.model_validate(case))


@router.put("/cases/{case_id}")
async def update_case(db: DBSession, case_id: int, data: TestCaseUpdate):
    """更新用例"""
    case = await case_service.update_case(db, case_id, data)
    return success(data=TestCaseResponse.model_validate(case))


@router.delete("/cases/{case_id}")
async def delete_case(db: DBSession, case_id: int):
    """删除用例"""
    await case_service.delete_case(db, case_id)
    return success(message="删除成功")


@router.post("/cases/{case_id}/copy")
async def copy_case(db: DBSession, case_id: int):
    """复制用例（包含断言和提取器）"""
    case = await case_service.copy_case(db, case_id)
    return success(data=TestCaseResponse.model_validate(case))


# ============ Assertion ============

@router.post("/cases/{case_id}/assertions")
async def create_assertion(db: DBSession, case_id: int, data: AssertionCreate):
    """添加断言"""
    assertion = await case_service.create_assertion(db, case_id, data)
    return success(data=AssertionResponse.model_validate(assertion))


@router.put("/assertions/{assertion_id}")
async def update_assertion(db: DBSession, assertion_id: int, data: AssertionUpdate):
    """更新断言"""
    assertion = await case_service.update_assertion(db, assertion_id, data)
    return success(data=AssertionResponse.model_validate(assertion))


@router.delete("/assertions/{assertion_id}")
async def delete_assertion(db: DBSession, assertion_id: int):
    """删除断言"""
    await case_service.delete_assertion(db, assertion_id)
    return success(message="删除成功")


# ============ Extractor ============

@router.post("/cases/{case_id}/extractors")
async def create_extractor(db: DBSession, case_id: int, data: ExtractorCreate):
    """添加提取器"""
    extractor = await case_service.create_extractor(db, case_id, data)
    return success(data=ExtractorResponse.model_validate(extractor))


@router.put("/extractors/{extractor_id}")
async def update_extractor(db: DBSession, extractor_id: int, data: ExtractorUpdate):
    """更新提取器"""
    extractor = await case_service.update_extractor(db, extractor_id, data)
    return success(data=ExtractorResponse.model_validate(extractor))


@router.delete("/extractors/{extractor_id}")
async def delete_extractor(db: DBSession, extractor_id: int):
    """删除提取器"""
    await case_service.delete_extractor(db, extractor_id)
    return success(message="删除成功")
