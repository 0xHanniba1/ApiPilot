from fastapi import APIRouter, Query

from app.api.deps import DBSession
from app.services import project_service
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.core.response import success, paginate

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("")
async def get_projects(
    db: DBSession,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """获取项目列表"""
    items, total = await project_service.get_projects(db, page, page_size)
    return paginate(
        items=[ProjectListResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("")
async def create_project(db: DBSession, data: ProjectCreate):
    """创建项目"""
    project = await project_service.create_project(db, data)
    return success(data=ProjectResponse.model_validate(project))


@router.get("/{project_id}")
async def get_project(db: DBSession, project_id: int):
    """获取项目详情"""
    project = await project_service.get_project_by_id(db, project_id)
    return success(data=ProjectResponse.model_validate(project))


@router.put("/{project_id}")
async def update_project(db: DBSession, project_id: int, data: ProjectUpdate):
    """更新项目"""
    project = await project_service.update_project(db, project_id, data)
    return success(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}")
async def delete_project(db: DBSession, project_id: int):
    """删除项目"""
    await project_service.delete_project(db, project_id)
    return success(message="删除成功")
