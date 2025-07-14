from celery import Celery
from app.core.config import settings

# Celery 앱 생성
celery_app = Celery(
    "academy_ai_assistant",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.excel_rebuilder"]
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30분
    task_soft_time_limit=25 * 60,  # 25분
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 태스크 라우팅
celery_app.conf.task_routes = {
    "app.workers.excel_rebuilder.*": {"queue": "excel_rebuilder"},
} 