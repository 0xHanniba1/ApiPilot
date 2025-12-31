from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success, ResponseModel
from app.models.project import Project
from app.models.test_case import TestCase
from app.models.test_suite import TestSuite
from app.models.execution import TestExecution, ExecutionDetail

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/dashboard", response_model=ResponseModel)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    首页统计数据

    返回：项目总数、用例总数、今日执行数、整体通过率
    """
    # 项目总数
    project_count = await db.scalar(select(func.count(Project.id)))

    # 用例总数
    case_count = await db.scalar(select(func.count(TestCase.id)))

    # 测试集总数
    suite_count = await db.scalar(select(func.count(TestSuite.id)))

    # 今日执行数
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_execution_count = await db.scalar(
        select(func.count(TestExecution.id)).where(
            TestExecution.created_at >= today_start
        )
    )

    # 今日通过/失败
    today_passed = await db.scalar(
        select(func.count(TestExecution.id)).where(
            and_(
                TestExecution.created_at >= today_start,
                TestExecution.status == "passed",
            )
        )
    )
    today_failed = await db.scalar(
        select(func.count(TestExecution.id)).where(
            and_(
                TestExecution.created_at >= today_start,
                TestExecution.status.in_(["failed", "error"]),
            )
        )
    )

    # 整体通过率（所有已完成的执行）
    total_executions = await db.scalar(
        select(func.count(TestExecution.id)).where(
            TestExecution.status.in_(["passed", "failed", "error"])
        )
    )
    total_passed = await db.scalar(
        select(func.count(TestExecution.id)).where(
            TestExecution.status == "passed"
        )
    )
    overall_pass_rate = round(total_passed / total_executions * 100, 1) if total_executions > 0 else 0

    # 近7天执行趋势
    week_ago = datetime.now() - timedelta(days=7)
    recent_executions = await db.scalar(
        select(func.count(TestExecution.id)).where(
            TestExecution.created_at >= week_ago
        )
    )

    return success(data={
        "project_count": project_count,
        "case_count": case_count,
        "suite_count": suite_count,
        "today_execution_count": today_execution_count,
        "today_passed": today_passed,
        "today_failed": today_failed,
        "overall_pass_rate": overall_pass_rate,
        "total_executions": total_executions,
        "recent_executions": recent_executions,
    })


@router.get("/projects/{project_id}/trend", response_model=ResponseModel)
async def get_project_trend(
    project_id: int,
    days: int = Query(7, ge=1, le=90, description="天数，默认7天，最大90天"),
    db: AsyncSession = Depends(get_db),
):
    """
    项目执行趋势

    返回指定天数内每天的执行数量、通过数、失败数
    """
    # 获取项目下的测试集ID
    suite_ids_stmt = select(TestSuite.id).where(TestSuite.project_id == project_id)
    suite_ids_result = await db.execute(suite_ids_stmt)
    suite_ids = [row[0] for row in suite_ids_result.all()]

    if not suite_ids:
        return success(data={"project_id": project_id, "days": days, "trend": []})

    # 计算日期范围
    end_date = datetime.now().replace(hour=23, minute=59, second=59)
    start_date = (datetime.now() - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0)

    # 查询每天的统计
    trend = []
    current_date = start_date

    while current_date <= end_date:
        day_start = current_date.replace(hour=0, minute=0, second=0)
        day_end = current_date.replace(hour=23, minute=59, second=59)

        # 当天执行总数
        total = await db.scalar(
            select(func.count(TestExecution.id)).where(
                and_(
                    TestExecution.suite_id.in_(suite_ids),
                    TestExecution.created_at >= day_start,
                    TestExecution.created_at <= day_end,
                )
            )
        )

        # 当天通过数
        passed = await db.scalar(
            select(func.count(TestExecution.id)).where(
                and_(
                    TestExecution.suite_id.in_(suite_ids),
                    TestExecution.created_at >= day_start,
                    TestExecution.created_at <= day_end,
                    TestExecution.status == "passed",
                )
            )
        )

        # 当天失败数
        failed = await db.scalar(
            select(func.count(TestExecution.id)).where(
                and_(
                    TestExecution.suite_id.in_(suite_ids),
                    TestExecution.created_at >= day_start,
                    TestExecution.created_at <= day_end,
                    TestExecution.status.in_(["failed", "error"]),
                )
            )
        )

        trend.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        })

        current_date += timedelta(days=1)

    return success(data={
        "project_id": project_id,
        "days": days,
        "trend": trend,
    })


@router.get("/cases/top-failures", response_model=ResponseModel)
async def get_top_failure_cases(
    project_id: int = Query(None, description="项目ID（可选）"),
    days: int = Query(30, ge=1, le=90, description="统计天数"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: AsyncSession = Depends(get_db),
):
    """
    失败率最高的用例 Top N

    返回指定时间范围内失败率最高的用例列表
    """
    start_date = datetime.now() - timedelta(days=days)

    # 构建基础查询
    base_conditions = [ExecutionDetail.executed_at >= start_date]

    # 如果指定了项目ID，需要关联查询
    if project_id:
        # 获取项目下的用例ID
        case_ids_stmt = (
            select(TestCase.id)
            .join(TestSuite, TestCase.module_id == TestSuite.id)
            .where(TestSuite.project_id == project_id)
        )
        # 这里简化处理，实际应该通过 module -> project 关联

    # 统计每个用例的执行次数和失败次数
    stmt = (
        select(
            ExecutionDetail.test_case_id,
            func.count(ExecutionDetail.id).label("total_count"),
            func.sum(
                case(
                    (ExecutionDetail.status.in_(["failed", "error"]), 1),
                    else_=0
                )
            ).label("failure_count"),
        )
        .where(ExecutionDetail.executed_at >= start_date)
        .group_by(ExecutionDetail.test_case_id)
        .having(func.count(ExecutionDetail.id) >= 1)  # 至少执行过1次
        .order_by(
            (func.sum(case((ExecutionDetail.status.in_(["failed", "error"]), 1), else_=0)) * 100.0 /
             func.count(ExecutionDetail.id)).desc()
        )
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # 获取用例详情
    case_ids = [row[0] for row in rows]
    if case_ids:
        cases_stmt = select(TestCase).where(TestCase.id.in_(case_ids))
        cases_result = await db.execute(cases_stmt)
        cases_map = {c.id: c for c in cases_result.scalars().all()}
    else:
        cases_map = {}

    items = []
    for row in rows:
        case_id, total_count, failure_count = row
        test_case = cases_map.get(case_id)
        failure_rate = round(failure_count / total_count * 100, 1) if total_count > 0 else 0

        items.append({
            "test_case_id": case_id,
            "test_case_name": test_case.name if test_case else None,
            "method": test_case.method if test_case else None,
            "path": test_case.path if test_case else None,
            "total_count": total_count,
            "failure_count": failure_count,
            "failure_rate": failure_rate,
        })

    return success(data={
        "days": days,
        "limit": limit,
        "items": items,
    })


@router.get("/suites/{suite_id}/history", response_model=ResponseModel)
async def get_suite_execution_history(
    suite_id: int,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
):
    """
    测试集执行历史

    返回测试集最近的执行记录和通过率变化
    """
    stmt = (
        select(TestExecution)
        .where(TestExecution.suite_id == suite_id)
        .order_by(TestExecution.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    executions = result.scalars().all()

    history = [
        {
            "id": e.id,
            "status": e.status,
            "total_count": e.total_count,
            "passed_count": e.passed_count,
            "failed_count": e.failed_count,
            "pass_rate": round(e.passed_count / e.total_count * 100, 1) if e.total_count > 0 else 0,
            "duration_ms": e.duration_ms,
            "trigger_type": e.trigger_type,
            "started_at": e.started_at,
            "finished_at": e.finished_at,
        }
        for e in executions
    ]

    # 计算平均通过率
    if history:
        avg_pass_rate = round(
            sum(h["pass_rate"] for h in history) / len(history), 1
        )
    else:
        avg_pass_rate = 0

    return success(data={
        "suite_id": suite_id,
        "total_executions": len(history),
        "avg_pass_rate": avg_pass_rate,
        "history": history,
    })
