from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Module, Project
from app.schemas import ModuleCreate, ModuleUpdate
from app.core.exceptions import NotFoundError, ValidationError


def build_module_tree(modules: list[Module], parent_id: int | None = None) -> list[dict]:
    """递归构建模块树"""
    tree = []
    for module in modules:
        if module.parent_id == parent_id:
            node = {
                "id": module.id,
                "name": module.name,
                "description": module.description,
                "parent_id": module.parent_id,
                "sort_order": module.sort_order,
                "children": build_module_tree(modules, module.id)
            }
            tree.append(node)
    # 按 sort_order 排序
    tree.sort(key=lambda x: x["sort_order"])
    return tree


async def get_module_tree(db: AsyncSession, project_id: int):
    # 验证项目存在
    project_stmt = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_stmt)
    if not project_result.scalar_one_or_none():
        raise NotFoundError(message="项目不存在", detail=f"project_id={project_id}")

    # 获取该项目所有模块
    stmt = select(Module).where(Module.project_id == project_id).order_by(Module.sort_order)
    result = await db.execute(stmt)
    modules = result.scalars().all()

    # 构建树形结构
    return build_module_tree(list(modules))


async def get_module_by_id(db: AsyncSession, module_id: int):
    stmt = select(Module).where(Module.id == module_id)
    result = await db.execute(stmt)
    module = result.scalar_one_or_none()

    if not module:
        raise NotFoundError(message="模块不存在", detail=f"module_id={module_id}")

    return module


async def create_module(db: AsyncSession, project_id: int, data: ModuleCreate):
    # 验证项目存在
    project_stmt = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_stmt)
    if not project_result.scalar_one_or_none():
        raise NotFoundError(message="项目不存在", detail=f"project_id={project_id}")

    # 如果指定了父模块，验证父模块存在且属于同一项目
    if data.parent_id:
        parent_stmt = select(Module).where(
            Module.id == data.parent_id,
            Module.project_id == project_id
        )
        parent_result = await db.execute(parent_stmt)
        if not parent_result.scalar_one_or_none():
            raise ValidationError(message="父模块不存在或不属于该项目", detail=f"parent_id={data.parent_id}")

    module = Module(project_id=project_id, **data.model_dump())
    db.add(module)
    await db.flush()
    await db.refresh(module)

    return module


async def update_module(db: AsyncSession, module_id: int, data: ModuleUpdate):
    module = await get_module_by_id(db, module_id)

    # 如果更新父模块，验证不能设置为自己或自己的子模块
    if data.parent_id is not None:
        if data.parent_id == module_id:
            raise ValidationError(message="不能将模块设置为自己的子模块")

        if data.parent_id:
            # 验证父模块存在且属于同一项目
            parent_stmt = select(Module).where(
                Module.id == data.parent_id,
                Module.project_id == module.project_id
            )
            parent_result = await db.execute(parent_stmt)
            if not parent_result.scalar_one_or_none():
                raise ValidationError(message="父模块不存在或不属于该项目")

            # 检查是否会形成循环（父模块不能是当前模块的子孙）
            if await is_descendant(db, data.parent_id, module_id):
                raise ValidationError(message="不能将模块移动到其子模块下")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)

    await db.flush()
    await db.refresh(module)

    return module


async def is_descendant(db: AsyncSession, child_id: int, ancestor_id: int) -> bool:
    """检查 child_id 是否是 ancestor_id 的子孙"""
    stmt = select(Module).where(Module.id == child_id)
    result = await db.execute(stmt)
    module = result.scalar_one_or_none()

    if not module:
        return False

    if module.parent_id == ancestor_id:
        return True

    if module.parent_id:
        return await is_descendant(db, module.parent_id, ancestor_id)

    return False


async def delete_module(db: AsyncSession, module_id: int):
    module = await get_module_by_id(db, module_id)

    # 递归删除所有子模块
    await delete_children(db, module_id)

    await db.delete(module)
    await db.flush()


async def delete_children(db: AsyncSession, parent_id: int):
    """递归删除所有子模块"""
    stmt = select(Module).where(Module.parent_id == parent_id)
    result = await db.execute(stmt)
    children = result.scalars().all()

    for child in children:
        await delete_children(db, child.id)
        await db.delete(child)
