from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Environment, EnvVariable, Project
from app.schemas import (
    EnvironmentCreate, EnvironmentUpdate,
    EnvVariableCreate, EnvVariableUpdate
)
from app.core.exceptions import NotFoundError, DuplicateError


# ============ Environment ============

async def get_environments(db: AsyncSession, project_id: int):
    # 验证项目存在
    project_stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(project_stmt)
    if not result.scalar_one_or_none():
        raise NotFoundError(message="项目不存在", detail=f"project_id={project_id}")

    stmt = select(Environment).where(Environment.project_id == project_id).order_by(Environment.id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_environment_by_id(db: AsyncSession, env_id: int, with_variables: bool = False):
    if with_variables:
        stmt = select(Environment).where(Environment.id == env_id).options(selectinload(Environment.variables))
    else:
        stmt = select(Environment).where(Environment.id == env_id)

    result = await db.execute(stmt)
    env = result.scalar_one_or_none()

    if not env:
        raise NotFoundError(message="环境不存在", detail=f"environment_id={env_id}")

    return env


async def create_environment(db: AsyncSession, project_id: int, data: EnvironmentCreate):
    # 验证项目存在
    project_stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(project_stmt)
    if not result.scalar_one_or_none():
        raise NotFoundError(message="项目不存在", detail=f"project_id={project_id}")

    # 检查同项目下环境名称是否重复
    stmt = select(Environment).where(
        Environment.project_id == project_id,
        Environment.name == data.name
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise DuplicateError(message="环境名称已存在", detail=f"name={data.name}")

    # 如果设置为默认环境，取消其他默认环境
    if data.is_default:
        await unset_default_environment(db, project_id)

    env = Environment(project_id=project_id, **data.model_dump())
    db.add(env)
    await db.flush()
    await db.refresh(env)

    return env


async def update_environment(db: AsyncSession, env_id: int, data: EnvironmentUpdate):
    env = await get_environment_by_id(db, env_id)

    # 检查名称是否重复
    if data.name and data.name != env.name:
        stmt = select(Environment).where(
            Environment.project_id == env.project_id,
            Environment.name == data.name
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise DuplicateError(message="环境名称已存在", detail=f"name={data.name}")

    # 如果设置为默认环境，取消其他默认环境
    if data.is_default:
        await unset_default_environment(db, env.project_id, exclude_id=env_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(env, field, value)

    await db.flush()
    await db.refresh(env)

    return env


async def delete_environment(db: AsyncSession, env_id: int):
    env = await get_environment_by_id(db, env_id)
    await db.delete(env)
    await db.flush()


async def unset_default_environment(db: AsyncSession, project_id: int, exclude_id: int = None):
    """取消项目下其他环境的默认状态"""
    stmt = select(Environment).where(
        Environment.project_id == project_id,
        Environment.is_default == True
    )
    if exclude_id:
        stmt = stmt.where(Environment.id != exclude_id)

    result = await db.execute(stmt)
    for env in result.scalars().all():
        env.is_default = False


# ============ Environment Variable ============

async def get_variable_by_id(db: AsyncSession, env_id: int, var_id: int):
    stmt = select(EnvVariable).where(
        EnvVariable.id == var_id,
        EnvVariable.environment_id == env_id
    )
    result = await db.execute(stmt)
    var = result.scalar_one_or_none()

    if not var:
        raise NotFoundError(message="环境变量不存在", detail=f"variable_id={var_id}")

    return var


async def create_variable(db: AsyncSession, env_id: int, data: EnvVariableCreate):
    # 验证环境存在
    await get_environment_by_id(db, env_id)

    # 检查变量名是否重复
    stmt = select(EnvVariable).where(
        EnvVariable.environment_id == env_id,
        EnvVariable.key == data.key
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise DuplicateError(message="变量名已存在", detail=f"key={data.key}")

    var = EnvVariable(environment_id=env_id, **data.model_dump())
    db.add(var)
    await db.flush()
    await db.refresh(var)

    return var


async def update_variable(db: AsyncSession, env_id: int, var_id: int, data: EnvVariableUpdate):
    var = await get_variable_by_id(db, env_id, var_id)

    # 检查变量名是否重复
    if data.key and data.key != var.key:
        stmt = select(EnvVariable).where(
            EnvVariable.environment_id == env_id,
            EnvVariable.key == data.key
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise DuplicateError(message="变量名已存在", detail=f"key={data.key}")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(var, field, value)

    await db.flush()
    await db.refresh(var)

    return var


async def delete_variable(db: AsyncSession, env_id: int, var_id: int):
    var = await get_variable_by_id(db, env_id, var_id)
    await db.delete(var)
    await db.flush()
