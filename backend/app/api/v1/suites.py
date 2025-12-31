from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success, paginate, ResponseModel, PaginationResponse
from app.schemas.test_suite import (
    TestSuiteCreate,
    TestSuiteUpdate,
    TestSuiteResponse,
    TestSuiteListResponse,
    TestSuiteDetailResponse,
    SuiteCaseCreate,
    SuiteCaseResponse,
    SuiteCaseOrderUpdate,
)
from app.services import suite_service

router = APIRouter(tags=["测试集"])


@router.get("/projects/{project_id}/suites", response_model=PaginationResponse)
async def get_suites(
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取项目的测试集列表"""
    suites, total = await suite_service.get_suites(
        db=db,
        project_id=project_id,
        page=page,
        page_size=page_size,
    )
    return paginate(items=suites, total=total, page=page, page_size=page_size)


@router.post("/projects/{project_id}/suites", response_model=ResponseModel)
async def create_suite(
    project_id: int,
    request: TestSuiteCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建测试集"""
    suite = await suite_service.create_suite(
        db=db,
        project_id=project_id,
        name=request.name,
        description=request.description,
        execution_mode=request.execution_mode,
    )
    return success(data=TestSuiteResponse.model_validate(suite))


@router.get("/suites/{suite_id}", response_model=ResponseModel)
async def get_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取测试集详情（包含用例列表）"""
    suite_data = await suite_service.get_suite(db=db, suite_id=suite_id)
    return success(data=suite_data)


@router.put("/suites/{suite_id}", response_model=ResponseModel)
async def update_suite(
    suite_id: int,
    request: TestSuiteUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新测试集"""
    suite = await suite_service.update_suite(
        db=db,
        suite_id=suite_id,
        name=request.name,
        description=request.description,
        execution_mode=request.execution_mode,
    )
    return success(data=TestSuiteResponse.model_validate(suite))


@router.delete("/suites/{suite_id}", response_model=ResponseModel)
async def delete_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除测试集"""
    await suite_service.delete_suite(db=db, suite_id=suite_id)
    return success(message="删除成功")


@router.post("/suites/{suite_id}/cases", response_model=ResponseModel)
async def add_case_to_suite(
    suite_id: int,
    request: SuiteCaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加用例到测试集"""
    suite_case = await suite_service.add_case_to_suite(
        db=db,
        suite_id=suite_id,
        test_case_id=request.test_case_id,
        sort_order=request.sort_order if request.sort_order > 0 else None,
    )
    return success(data=SuiteCaseResponse.model_validate(suite_case))


@router.delete("/suites/{suite_id}/cases/{case_id}", response_model=ResponseModel)
async def remove_case_from_suite(
    suite_id: int,
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """从测试集移除用例"""
    await suite_service.remove_case_from_suite(
        db=db,
        suite_id=suite_id,
        case_id=case_id,
    )
    return success(message="移除成功")


@router.put("/suites/{suite_id}/cases/order", response_model=ResponseModel)
async def update_cases_order(
    suite_id: int,
    request: SuiteCaseOrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    """调整用例顺序"""
    await suite_service.update_cases_order(
        db=db,
        suite_id=suite_id,
        case_orders=request.case_orders,
    )
    return success(message="排序更新成功")
