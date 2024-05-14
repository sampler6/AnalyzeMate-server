from celery.app import Celery
from config import LOAD_SECURITIES, REDIS_HOST

from task.task_register import register_dev_accounts
from task.task_upload import upload_data_from_files

app_celery = Celery(
    "task",
    broker=f"redis://{REDIS_HOST}:6379",
    backend=f"redis://{REDIS_HOST}:6379",
    broker_connection_retry_on_startup=True,
)

if LOAD_SECURITIES:
    app_celery.conf.beat_schedule = {
        "strategy": {"task": "task.task_strategy.start_strategy", "schedule": 300.0, "args": ()},
    }
    upload_data_from_files.delay()
register_dev_accounts.delay()
