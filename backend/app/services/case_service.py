from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import TestCase, Assertion, Extractor, Module
from app.schemas import (
    TestCaseCreate, TestCaseUpdate,
    AssertionCreate, AssertionUpdate,
    ExtractorCreate, ExtractorUpdate
)
from app.core.exceptions import NotFoundError


# ============ Test Case ============

async def get_cases(db: AsyncSession, module_id: int, page: int = 1, page_size: int = 20):
    # 验证模块存在
    module_stmt = select(Module).where(Module.id == module_id)
    result = await db.execute(module_stmt)
    if not result.scalar_one_or_none():
        raise NotFoundError(message="模块不存在", detail=f"module_id={module_id}")

    # 计算总数
    count_stmt = select(func.count(TestCase.id)).where(TestCase.module_id == module_id)
    total = await db.scalar(count_stmt)

    # 分页查询
    offset = (page - 1) * page_size
    stmt = (
        select(TestCase)
        .where(TestCase.module_id == module_id)
        .order_by(TestCase.sort_order, TestCase.id)
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    return items, total


async def get_case_by_id(db: AsyncSession, case_id: int, with_details: bool = False):
    if with_details:
        stmt = (
            select(TestCase)
            .where(TestCase.id == case_id)
            .options(
                selectinload(TestCase.assertions),
                selectinload(TestCase.extractors)
            )
        )
    else:
        stmt = select(TestCase).where(TestCase.id == case_id)

    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        raise NotFoundError(message="用例不存在", detail=f"case_id={case_id}")

    return case


async def create_case(db: AsyncSession, module_id: int, data: TestCaseCreate):
    # 验证模块存在
    module_stmt = select(Module).where(Module.id == module_id)
    result = await db.execute(module_stmt)
    if not result.scalar_one_or_none():
        raise NotFoundError(message="模块不存在", detail=f"module_id={module_id}")

    case = TestCase(module_id=module_id, **data.model_dump())
    db.add(case)
    await db.flush()
    await db.refresh(case)

    return case


async def update_case(db: AsyncSession, case_id: int, data: TestCaseUpdate):
    case = await get_case_by_id(db, case_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.flush()
    await db.refresh(case)

    return case


async def delete_case(db: AsyncSession, case_id: int):
    case = await get_case_by_id(db, case_id)
    await db.delete(case)
    await db.flush()


async def copy_case(db: AsyncSession, case_id: int):
    """复制用例（包含断言和提取器）"""
    case = await get_case_by_id(db, case_id, with_details=True)

    # 创建用例副本
    new_case = TestCase(
        module_id=case.module_id,
        name=f"{case.name} (副本)",
        description=case.description,
        method=case.method,
        path=case.path,
        headers=case.headers,
        params=case.params,
        body_type=case.body_type,
        body_content=case.body_content,
        pre_script=case.pre_script,
        post_script=case.post_script,
        timeout=case.timeout,
        retry_count=case.retry_count,
        is_active=case.is_active,
        sort_order=case.sort_order,
    )
    db.add(new_case)
    await db.flush()

    # 复制断言
    for assertion in case.assertions:
        new_assertion = Assertion(
            test_case_id=new_case.id,
            name=assertion.name,
            type=assertion.type,
            expression=assertion.expression,
            operator=assertion.operator,
            expected_value=assertion.expected_value,
            sort_order=assertion.sort_order,
        )
        db.add(new_assertion)

    # 复制提取器
    for extractor in case.extractors:
        new_extractor = Extractor(
            test_case_id=new_case.id,
            name=extractor.name,
            source=extractor.source,
            expression=extractor.expression,
            variable_name=extractor.variable_name,
            default_value=extractor.default_value,
            sort_order=extractor.sort_order,
        )
        db.add(new_extractor)

    await db.flush()
    await db.refresh(new_case)

    return new_case


# ============ Assertion ============

async def get_assertion_by_id(db: AsyncSession, assertion_id: int):
    stmt = select(Assertion).where(Assertion.id == assertion_id)
    result = await db.execute(stmt)
    assertion = result.scalar_one_or_none()

    if not assertion:
        raise NotFoundError(message="断言不存在", detail=f"assertion_id={assertion_id}")

    return assertion


async def create_assertion(db: AsyncSession, case_id: int, data: AssertionCreate):
    # 验证用例存在
    await get_case_by_id(db, case_id)

    assertion = Assertion(test_case_id=case_id, **data.model_dump())
    db.add(assertion)
    await db.flush()
    await db.refresh(assertion)

    return assertion


async def update_assertion(db: AsyncSession, assertion_id: int, data: AssertionUpdate):
    assertion = await get_assertion_by_id(db, assertion_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assertion, field, value)

    await db.flush()
    await db.refresh(assertion)

    return assertion


async def delete_assertion(db: AsyncSession, assertion_id: int):
    assertion = await get_assertion_by_id(db, assertion_id)
    await db.delete(assertion)
    await db.flush()


# ============ Extractor ============

async def get_extractor_by_id(db: AsyncSession, extractor_id: int):
    stmt = select(Extractor).where(Extractor.id == extractor_id)
    result = await db.execute(stmt)
    extractor = result.scalar_one_or_none()

    if not extractor:
        raise NotFoundError(message="提取器不存在", detail=f"extractor_id={extractor_id}")

    return extractor


async def create_extractor(db: AsyncSession, case_id: int, data: ExtractorCreate):
    # 验证用例存在
    await get_case_by_id(db, case_id)

    extractor = Extractor(test_case_id=case_id, **data.model_dump())
    db.add(extractor)
    await db.flush()
    await db.refresh(extractor)

    return extractor


async def update_extractor(db: AsyncSession, extractor_id: int, data: ExtractorUpdate):
    extractor = await get_extractor_by_id(db, extractor_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(extractor, field, value)

    await db.flush()
    await db.refresh(extractor)

    return extractor


async def delete_extractor(db: AsyncSession, extractor_id: int):
    extractor = await get_extractor_by_id(db, extractor_id)
    await db.delete(extractor)
    await db.flush()
