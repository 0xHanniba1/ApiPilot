from fastapi import APIRouter

from app.api.deps import DBSession
from app.services import module_service
from app.schemas import ModuleCreate, ModuleUpdate, ModuleResponse
from app.core.response import success

router = APIRouter(tags=["模块管理"])


@router.get("/projects/{project_id}/modules")
async def get_module_tree(db: DBSession, project_id: int):
    """获取项目的模块树"""
    tree = await module_service.get_module_tree(db, project_id)
    return success(data=tree)


@router.post("/projects/{project_id}/modules")
async def create_module(db: DBSession, project_id: int, data: ModuleCreate):
    """创建模块"""
    module = await module_service.create_module(db, project_id, data)
    return success(data=ModuleResponse.model_validate(module))


@router.put("/modules/{module_id}")
async def update_module(db: DBSession, module_id: int, data: ModuleUpdate):
    """更新模块"""
    module = await module_service.update_module(db, module_id, data)
    return success(data=ModuleResponse.model_validate(module))


@router.delete("/modules/{module_id}")
async def delete_module(db: DBSession, module_id: int):
    """删除模块（级联删除子模块）"""
    await module_service.delete_module(db, module_id)
    return success(message="删除成功")
