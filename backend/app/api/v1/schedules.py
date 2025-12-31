from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success, paginate, ResponseModel, PaginationResponse
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleListResponse,
)
from app.services import schedule_service

router = APIRouter(prefix="/schedules", tags=["定时任务"])


@router.get("", response_model=PaginationResponse)
async def get_schedules(
    suite_id: int = Query(None, description="测试集ID"),
    is_active: bool = Query(None, description="是否启用"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取定时任务列表"""
    items, total = await schedule_service.get_schedules(
        db=db,
        suite_id=suite_id,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    return paginate(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
async def create_schedule(
    request: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建定时任务"""
    schedule = await schedule_service.create_schedule(
        db=db,
        name=request.name,
        suite_id=request.suite_id,
        environment_id=request.environment_id,
        cron_expression=request.cron_expression,
        is_active=request.is_active,
        notify_on_failure=request.notify_on_failure,
        notify_emails=request.notify_emails,
    )
    return success(data=ScheduleResponse.model_validate(schedule))


@router.get("/{schedule_id}", response_model=ResponseModel)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取定时任务详情"""
    schedule = await schedule_service.get_schedule(db=db, schedule_id=schedule_id)

    return success(data={
        "id": schedule.id,
        "name": schedule.name,
        "suite_id": schedule.suite_id,
        "suite_name": schedule.test_suite.name if schedule.test_suite else None,
        "environment_id": schedule.environment_id,
        "environment_name": schedule.environment.name if schedule.environment else None,
        "cron_expression": schedule.cron_expression,
        "is_active": schedule.is_active,
        "notify_on_failure": schedule.notify_on_failure,
        "notify_emails": schedule.notify_emails,
        "last_run_at": schedule.last_run_at,
        "next_run_at": schedule.next_run_at,
        "created_at": schedule.created_at,
        "updated_at": schedule.updated_at,
    })


@router.put("/{schedule_id}", response_model=ResponseModel)
async def update_schedule(
    schedule_id: int,
    request: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新定时任务"""
    schedule = await schedule_service.update_schedule(
        db=db,
        schedule_id=schedule_id,
        name=request.name,
        suite_id=request.suite_id,
        environment_id=request.environment_id,
        cron_expression=request.cron_expression,
        is_active=request.is_active,
        notify_on_failure=request.notify_on_failure,
        notify_emails=request.notify_emails,
    )
    return success(data=ScheduleResponse.model_validate(schedule))


@router.delete("/{schedule_id}", response_model=ResponseModel)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除定时任务"""
    await schedule_service.delete_schedule(db=db, schedule_id=schedule_id)
    return success(message="删除成功")


@router.post("/{schedule_id}/toggle", response_model=ResponseModel)
async def toggle_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """启用/禁用定时任务"""
    schedule = await schedule_service.toggle_schedule(db=db, schedule_id=schedule_id)
    return success(
        data=ScheduleResponse.model_validate(schedule),
        message=f"任务已{'启用' if schedule.is_active else '禁用'}",
    )
