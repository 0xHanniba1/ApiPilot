from fastapi import APIRouter

from app.api.deps import DBSession
from app.services import environment_service
from app.schemas import (
    EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse, EnvironmentDetailResponse,
    EnvVariableCreate, EnvVariableUpdate, EnvVariableResponse
)
from app.core.response import success

router = APIRouter(tags=["环境管理"])


# ============ Environment ============

@router.get("/projects/{project_id}/environments")
async def get_environments(db: DBSession, project_id: int):
    """获取项目的环境列表"""
    items = await environment_service.get_environments(db, project_id)
    return success(data=[EnvironmentResponse.model_validate(item) for item in items])


@router.post("/projects/{project_id}/environments")
async def create_environment(db: DBSession, project_id: int, data: EnvironmentCreate):
    """创建环境"""
    env = await environment_service.create_environment(db, project_id, data)
    return success(data=EnvironmentResponse.model_validate(env))


@router.get("/environments/{env_id}")
async def get_environment(db: DBSession, env_id: int):
    """获取环境详情（包含变量列表）"""
    env = await environment_service.get_environment_by_id(db, env_id, with_variables=True)
    return success(data=EnvironmentDetailResponse.model_validate(env))


@router.put("/environments/{env_id}")
async def update_environment(db: DBSession, env_id: int, data: EnvironmentUpdate):
    """更新环境"""
    env = await environment_service.update_environment(db, env_id, data)
    return success(data=EnvironmentResponse.model_validate(env))


@router.delete("/environments/{env_id}")
async def delete_environment(db: DBSession, env_id: int):
    """删除环境"""
    await environment_service.delete_environment(db, env_id)
    return success(message="删除成功")


# ============ Environment Variable ============

@router.post("/environments/{env_id}/variables")
async def create_variable(db: DBSession, env_id: int, data: EnvVariableCreate):
    """添加环境变量"""
    var = await environment_service.create_variable(db, env_id, data)
    return success(data=EnvVariableResponse.model_validate(var))


@router.put("/environments/{env_id}/variables/{var_id}")
async def update_variable(db: DBSession, env_id: int, var_id: int, data: EnvVariableUpdate):
    """更新环境变量"""
    var = await environment_service.update_variable(db, env_id, var_id, data)
    return success(data=EnvVariableResponse.model_validate(var))


@router.delete("/environments/{env_id}/variables/{var_id}")
async def delete_variable(db: DBSession, env_id: int, var_id: int):
    """删除环境变量"""
    await environment_service.delete_variable(db, env_id, var_id)
    return success(message="删除成功")
