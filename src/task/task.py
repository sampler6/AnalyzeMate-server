from celery.app import Celery
from config import REDIS_HOST

app_celery = Celery(
    "task",
    broker=f"redis://{REDIS_HOST}:6379",
    backend=f"redis://{REDIS_HOST}:6379",
    broker_connection_retry_on_startup=True,
)


app_celery.conf.beat_schedule = {
    "strategy": {"task": "task.task_strategy.start_strategy", "schedule": 300.0, "args": ()},
}
