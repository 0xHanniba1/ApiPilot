from celery import Celery

from app.config import settings

celery_app = Celery(
    "apipilot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["celery_app.tasks.execution"],
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    
    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,
    
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
    },
    
    # 任务默认队列
    task_default_queue="default",
)
