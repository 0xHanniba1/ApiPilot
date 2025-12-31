from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker, selectinload
from croniter import croniter

from app.config import settings
from app.models.schedule import Schedule
from app.models.execution import TestExecution
from celery_app.tasks.execution import execute_suite_task

logger = get_task_logger(__name__)

# 创建同步数据库引擎
sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2")
sync_engine = create_engine(sync_database_url, pool_pre_ping=True)
SyncSession = sessionmaker(bind=sync_engine)


@shared_task(name="celery_app.tasks.schedule.check_due_schedules")
def check_due_schedules():
    """
    检查并触发到期的定时任务
    
    由 Celery Beat 每分钟调用一次
    """
    logger.info("开始检查定时任务...")
    
    with SyncSession() as db:
        now = datetime.now()
        
        # 查询需要执行的定时任务
        stmt = (
            select(Schedule)
            .where(
                Schedule.is_active == True,
                Schedule.next_run_at <= now,
            )
        )
        schedules = db.execute(stmt).scalars().all()
        
        if not schedules:
            logger.info("没有需要执行的定时任务")
            return {"triggered": 0}
        
        triggered_count = 0
        for schedule in schedules:
            try:
                # 创建执行记录
                execution = TestExecution(
                    suite_id=schedule.suite_id,
                    environment_id=schedule.environment_id,
                    trigger_type="schedule",
                    status="pending",
                    total_count=0,
                    passed_count=0,
                    failed_count=0,
                    skipped_count=0,
                )
                db.add(execution)
                db.flush()
                
                # 更新定时任务状态
                schedule.last_run_at = now
                schedule.next_run_at = _calculate_next_run(schedule.cron_expression)
                
                db.commit()
                
                # 触发执行任务
                execute_suite_task.delay(execution.id)
                
                logger.info(
                    f"触发定时任务: schedule_id={schedule.id}, "
                    f"name={schedule.name}, execution_id={execution.id}"
                )
                triggered_count += 1
                
            except Exception as e:
                logger.error(f"触发定时任务失败: schedule_id={schedule.id}, error={str(e)}")
                db.rollback()
        
        logger.info(f"定时任务检查完成，触发了 {triggered_count} 个任务")
        return {"triggered": triggered_count}


def _calculate_next_run(cron_expression: str) -> datetime:
    """计算下次执行时间"""
    try:
        cron = croniter(cron_expression, datetime.now())
        return cron.get_next(datetime)
    except Exception:
        return None
