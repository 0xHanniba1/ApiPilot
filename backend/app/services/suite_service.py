from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.test_suite import TestSuite, SuiteCase
from app.models.test_case import TestCase
from app.models.project import Project
from app.core.exceptions import NotFoundError, ValidationError, DuplicateError


async def get_suites(
    db: AsyncSession,
    project_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """获取项目的测试集列表"""
    # 验证项目存在
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError(f"项目不存在: {project_id}")

    # 查询测试集及用例数量
    stmt = (
        select(
            TestSuite,
            func.count(SuiteCase.id).label("case_count")
        )
        .outerjoin(SuiteCase, TestSuite.id == SuiteCase.suite_id)
        .where(TestSuite.project_id == project_id)
        .group_by(TestSuite.id)
        .order_by(TestSuite.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # 查询总数
    count_stmt = select(func.count(TestSuite.id)).where(TestSuite.project_id == project_id)
    total = await db.scalar(count_stmt)

    # 构建响应
    suites = []
    for suite, case_count in rows:
        suites.append({
            "id": suite.id,
            "project_id": suite.project_id,
            "name": suite.name,
            "description": suite.description,
            "execution_mode": suite.execution_mode,
            "case_count": case_count,
            "created_at": suite.created_at,
        })

    return suites, total


async def create_suite(
    db: AsyncSession,
    project_id: int,
    name: str,
    description: str = None,
    execution_mode: str = "sequential",
) -> TestSuite:
    """创建测试集"""
    # 验证项目存在
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError(f"项目不存在: {project_id}")

    # 检查名称重复
    stmt = select(TestSuite).where(
        TestSuite.project_id == project_id,
        TestSuite.name == name,
    )
    existing = await db.scalar(stmt)
    if existing:
        raise DuplicateError(f"测试集名称已存在: {name}")

    suite = TestSuite(
        project_id=project_id,
        name=name,
        description=description,
        execution_mode=execution_mode,
    )
    db.add(suite)
    await db.commit()
    await db.refresh(suite)

    return suite


async def get_suite(db: AsyncSession, suite_id: int) -> dict:
    """获取测试集详情（包含用例列表）"""
    stmt = (
        select(TestSuite)
        .where(TestSuite.id == suite_id)
        .options(
            selectinload(TestSuite.suite_cases).selectinload(SuiteCase.test_case)
        )
    )
    result = await db.execute(stmt)
    suite = result.scalar_one_or_none()

    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    # 按 sort_order 排序用例
    sorted_cases = sorted(suite.suite_cases, key=lambda x: x.sort_order)

    return {
        "id": suite.id,
        "project_id": suite.project_id,
        "name": suite.name,
        "description": suite.description,
        "execution_mode": suite.execution_mode,
        "created_at": suite.created_at,
        "updated_at": suite.updated_at,
        "cases": [
            {
                "id": sc.id,
                "suite_id": sc.suite_id,
                "test_case_id": sc.test_case_id,
                "sort_order": sc.sort_order,
                "test_case": {
                    "id": sc.test_case.id,
                    "module_id": sc.test_case.module_id,
                    "name": sc.test_case.name,
                    "method": sc.test_case.method,
                    "path": sc.test_case.path,
                    "is_active": sc.test_case.is_active,
                    "sort_order": sc.test_case.sort_order,
                    "created_at": sc.test_case.created_at,
                }
            }
            for sc in sorted_cases
        ],
    }


async def update_suite(
    db: AsyncSession,
    suite_id: int,
    name: str = None,
    description: str = None,
    execution_mode: str = None,
) -> TestSuite:
    """更新测试集"""
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    # 检查名称重复
    if name and name != suite.name:
        stmt = select(TestSuite).where(
            TestSuite.project_id == suite.project_id,
            TestSuite.name == name,
            TestSuite.id != suite_id,
        )
        existing = await db.scalar(stmt)
        if existing:
            raise DuplicateError(f"测试集名称已存在: {name}")
        suite.name = name

    if description is not None:
        suite.description = description
    if execution_mode is not None:
        suite.execution_mode = execution_mode

    await db.commit()
    await db.refresh(suite)

    return suite


async def delete_suite(db: AsyncSession, suite_id: int) -> None:
    """删除测试集"""
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    await db.delete(suite)
    await db.commit()


async def add_case_to_suite(
    db: AsyncSession,
    suite_id: int,
    test_case_id: int,
    sort_order: int = None,
) -> SuiteCase:
    """添加用例到测试集"""
    # 验证测试集存在
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    # 验证用例存在
    test_case = await db.get(TestCase, test_case_id)
    if not test_case:
        raise NotFoundError(f"用例不存在: {test_case_id}")

    # 检查是否已添加
    stmt = select(SuiteCase).where(
        SuiteCase.suite_id == suite_id,
        SuiteCase.test_case_id == test_case_id,
    )
    existing = await db.scalar(stmt)
    if existing:
        raise DuplicateError(f"用例已在测试集中: {test_case_id}")

    # 如果未指定排序，放到最后
    if sort_order is None:
        max_order_stmt = select(func.max(SuiteCase.sort_order)).where(
            SuiteCase.suite_id == suite_id
        )
        max_order = await db.scalar(max_order_stmt)
        sort_order = (max_order or 0) + 1

    suite_case = SuiteCase(
        suite_id=suite_id,
        test_case_id=test_case_id,
        sort_order=sort_order,
    )
    db.add(suite_case)
    await db.commit()
    await db.refresh(suite_case)

    return suite_case


async def remove_case_from_suite(
    db: AsyncSession,
    suite_id: int,
    case_id: int,
) -> None:
    """从测试集移除用例"""
    stmt = select(SuiteCase).where(
        SuiteCase.suite_id == suite_id,
        SuiteCase.test_case_id == case_id,
    )
    suite_case = await db.scalar(stmt)
    if not suite_case:
        raise NotFoundError(f"用例不在测试集中: {case_id}")

    await db.delete(suite_case)
    await db.commit()


async def update_cases_order(
    db: AsyncSession,
    suite_id: int,
    case_orders: list[dict],
) -> None:
    """
    调整用例顺序

    Args:
        case_orders: [{"test_case_id": 1, "sort_order": 0}, ...]
    """
    # 验证测试集存在
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    for item in case_orders:
        test_case_id = item.get("test_case_id")
        sort_order = item.get("sort_order", 0)

        stmt = select(SuiteCase).where(
            SuiteCase.suite_id == suite_id,
            SuiteCase.test_case_id == test_case_id,
        )
        suite_case = await db.scalar(stmt)
        if suite_case:
            suite_case.sort_order = sort_order

    await db.commit()


async def batch_add_cases(
    db: AsyncSession,
    suite_id: int,
    test_case_ids: list[int],
) -> list[SuiteCase]:
    """批量添加用例到测试集"""
    # 验证测试集存在
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    # 获取当前最大排序
    max_order_stmt = select(func.max(SuiteCase.sort_order)).where(
        SuiteCase.suite_id == suite_id
    )
    max_order = await db.scalar(max_order_stmt) or 0

    # 获取已存在的用例ID
    existing_stmt = select(SuiteCase.test_case_id).where(
        SuiteCase.suite_id == suite_id
    )
    result = await db.execute(existing_stmt)
    existing_ids = set(row[0] for row in result.all())

    added = []
    for i, case_id in enumerate(test_case_ids):
        if case_id in existing_ids:
            continue

        # 验证用例存在
        test_case = await db.get(TestCase, case_id)
        if not test_case:
            continue

        suite_case = SuiteCase(
            suite_id=suite_id,
            test_case_id=case_id,
            sort_order=max_order + i + 1,
        )
        db.add(suite_case)
        added.append(suite_case)

    await db.commit()
    for sc in added:
        await db.refresh(sc)

    return added
