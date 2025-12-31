from datetime import datetime

from croniter import croniter
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schedule import Schedule
from app.models.test_suite import TestSuite
from app.models.environment import Environment
from app.core.exceptions import NotFoundError, ValidationError


def calculate_next_run(cron_expression: str, base_time: datetime = None) -> datetime:
    """计算下次执行时间"""
    if base_time is None:
        base_time = datetime.now()
    try:
        cron = croniter(cron_expression, base_time)
        return cron.get_next(datetime)
    except Exception as e:
        raise ValidationError(f"无效的 Cron 表达式: {cron_expression}")


def validate_cron_expression(cron_expression: str) -> bool:
    """验证 Cron 表达式"""
    try:
        croniter(cron_expression)
        return True
    except Exception:
        return False


async def get_schedules(
    db: AsyncSession,
    suite_id: int = None,
    is_active: bool = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """获取定时任务列表"""
    stmt = (
        select(Schedule)
        .options(
            selectinload(Schedule.test_suite),
            selectinload(Schedule.environment),
        )
    )
    count_stmt = select(func.count(Schedule.id))

    if suite_id:
        stmt = stmt.where(Schedule.suite_id == suite_id)
        count_stmt = count_stmt.where(Schedule.suite_id == suite_id)

    if is_active is not None:
        stmt = stmt.where(Schedule.is_active == is_active)
        count_stmt = count_stmt.where(Schedule.is_active == is_active)

    stmt = stmt.order_by(Schedule.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    schedules = result.scalars().all()

    total = await db.scalar(count_stmt)

    items = [
        {
            "id": s.id,
            "name": s.name,
            "suite_id": s.suite_id,
            "suite_name": s.test_suite.name if s.test_suite else None,
            "environment_id": s.environment_id,
            "environment_name": s.environment.name if s.environment else None,
            "cron_expression": s.cron_expression,
            "is_active": s.is_active,
            "last_run_at": s.last_run_at,
            "next_run_at": s.next_run_at,
        }
        for s in schedules
    ]

    return items, total


async def create_schedule(
    db: AsyncSession,
    name: str,
    suite_id: int,
    environment_id: int,
    cron_expression: str,
    is_active: bool = True,
    notify_on_failure: bool = True,
    notify_emails: str = None,
) -> Schedule:
    """创建定时任务"""
    # 验证测试集存在
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise NotFoundError(f"测试集不存在: {suite_id}")

    # 验证环境存在
    environment = await db.get(Environment, environment_id)
    if not environment:
        raise NotFoundError(f"环境不存在: {environment_id}")

    # 验证 Cron 表达式
    if not validate_cron_expression(cron_expression):
        raise ValidationError(f"无效的 Cron 表达式: {cron_expression}")

    # 计算下次执行时间
    next_run_at = calculate_next_run(cron_expression) if is_active else None

    schedule = Schedule(
        name=name,
        suite_id=suite_id,
        environment_id=environment_id,
        cron_expression=cron_expression,
        is_active=is_active,
        notify_on_failure=notify_on_failure,
        notify_emails=notify_emails,
        next_run_at=next_run_at,
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return schedule


async def get_schedule(db: AsyncSession, schedule_id: int) -> Schedule:
    """获取定时任务详情"""
    stmt = (
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(
            selectinload(Schedule.test_suite),
            selectinload(Schedule.environment),
        )
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise NotFoundError(f"定时任务不存在: {schedule_id}")

    return schedule


async def update_schedule(
    db: AsyncSession,
    schedule_id: int,
    name: str = None,
    suite_id: int = None,
    environment_id: int = None,
    cron_expression: str = None,
    is_active: bool = None,
    notify_on_failure: bool = None,
    notify_emails: str = None,
) -> Schedule:
    """更新定时任务"""
    schedule = await db.get(Schedule, schedule_id)
    if not schedule:
        raise NotFoundError(f"定时任务不存在: {schedule_id}")

    if name is not None:
        schedule.name = name

    if suite_id is not None:
        suite = await db.get(TestSuite, suite_id)
        if not suite:
            raise NotFoundError(f"测试集不存在: {suite_id}")
        schedule.suite_id = suite_id

    if environment_id is not None:
        environment = await db.get(Environment, environment_id)
        if not environment:
            raise NotFoundError(f"环境不存在: {environment_id}")
        schedule.environment_id = environment_id

    if cron_expression is not None:
        if not validate_cron_expression(cron_expression):
            raise ValidationError(f"无效的 Cron 表达式: {cron_expression}")
        schedule.cron_expression = cron_expression

    if notify_on_failure is not None:
        schedule.notify_on_failure = notify_on_failure

    if notify_emails is not None:
        schedule.notify_emails = notify_emails

    if is_active is not None:
        schedule.is_active = is_active

    # 重新计算下次执行时间
    if schedule.is_active:
        schedule.next_run_at = calculate_next_run(schedule.cron_expression)
    else:
        schedule.next_run_at = None

    await db.commit()
    await db.refresh(schedule)

    return schedule


async def delete_schedule(db: AsyncSession, schedule_id: int) -> None:
    """删除定时任务"""
    schedule = await db.get(Schedule, schedule_id)
    if not schedule:
        raise NotFoundError(f"定时任务不存在: {schedule_id}")

    await db.delete(schedule)
    await db.commit()


async def toggle_schedule(db: AsyncSession, schedule_id: int) -> Schedule:
    """启用/禁用定时任务"""
    schedule = await db.get(Schedule, schedule_id)
    if not schedule:
        raise NotFoundError(f"定时任务不存在: {schedule_id}")

    schedule.is_active = not schedule.is_active

    if schedule.is_active:
        schedule.next_run_at = calculate_next_run(schedule.cron_expression)
    else:
        schedule.next_run_at = None

    await db.commit()
    await db.refresh(schedule)

    return schedule


async def get_due_schedules(db: AsyncSession) -> list[Schedule]:
    """获取需要执行的定时任务"""
    now = datetime.now()
    stmt = (
        select(Schedule)
        .where(
            Schedule.is_active == True,
            Schedule.next_run_at <= now,
        )
        .options(
            selectinload(Schedule.test_suite),
            selectinload(Schedule.environment),
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_schedule_after_run(
    db: AsyncSession,
    schedule_id: int,
) -> None:
    """执行后更新定时任务状态"""
    schedule = await db.get(Schedule, schedule_id)
    if schedule:
        schedule.last_run_at = datetime.now()
        schedule.next_run_at = calculate_next_run(schedule.cron_expression)
        await db.commit()
