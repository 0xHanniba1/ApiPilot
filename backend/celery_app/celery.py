from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "apipilot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["celery_app.tasks.execution", "celery_app.tasks.schedule"],
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # 时区
    timezone="Asia/Shanghai",
    enable_utc=False,  # 使用本地时间

    # 任务结果
    result_expires=3600,  # 结果过期时间 1 小时

    # 任务执行
    task_acks_late=True,  # 任务执行完成后再确认
    task_reject_on_worker_lost=True,  # Worker 丢失时拒绝任务

    # 并发
    worker_prefetch_multiplier=1,  # 每次只取一个任务
    worker_concurrency=4,  # 并发数

    # 任务路由
    task_routes={
        "celery_app.tasks.execution.*": {"queue": "execution"},
        "celery_app.tasks.schedule.*": {"queue": "default"},
    },

    # 任务默认队列
    task_default_queue="default",

    # Beat 定时任务配置
    beat_schedule={
        # 每分钟检查一次需要执行的定时任务
        "check-due-schedules": {
            "task": "celery_app.tasks.schedule.check_due_schedules",
            "schedule": 60.0,  # 每 60 秒执行一次
        },
    },
)
