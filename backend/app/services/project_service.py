from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate
from app.core.exceptions import NotFoundError, DuplicateError


async def get_projects(db: AsyncSession, page: int = 1, page_size: int = 20):
    # 计算总数
    count_stmt = select(func.count(Project.id))
    total = await db.scalar(count_stmt)

    # 分页查询
    offset = (page - 1) * page_size
    stmt = select(Project).order_by(Project.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return items, total


async def get_project_by_id(db: AsyncSession, project_id: int):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise NotFoundError(message="项目不存在", detail=f"project_id={project_id}")

    return project


async def create_project(db: AsyncSession, data: ProjectCreate):
    # 检查名称是否重复
    stmt = select(Project).where(Project.name == data.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise DuplicateError(message="项目名称已存在", detail=f"name={data.name}")

    project = Project(**data.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)

    return project


async def update_project(db: AsyncSession, project_id: int, data: ProjectUpdate):
    project = await get_project_by_id(db, project_id)

    # 如果更新名称，检查是否重复
    if data.name and data.name != project.name:
        stmt = select(Project).where(Project.name == data.name)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise DuplicateError(message="项目名称已存在", detail=f"name={data.name}")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.flush()
    await db.refresh(project)

    return project


async def delete_project(db: AsyncSession, project_id: int):
    project = await get_project_by_id(db, project_id)
    await db.delete(project)
    await db.flush()
