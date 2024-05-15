from time import sleep

from celery.app import Celery
from config import LOAD_SECURITIES, REDIS_HOST

from task.task_get_new_candles import get_new_candles  # noqa

# Порядок import важен
from task.task_register import register_dev_accounts  # noqa
from task.task_send_notification import send_notification  # noqa
from task.task_strategy import start_strategy  # noqa
from task.task_upload import upload_data_from_files  # noqa

app_celery = Celery(
    "task",
    broker=f"redis://{REDIS_HOST}:6379",
    backend=f"redis://{REDIS_HOST}:6379",
    broker_connection_retry_on_startup=True,
)

if LOAD_SECURITIES:
    upload_data_from_files.delay()
    app_celery.conf.beat_schedule = {
        "strategy": {"task": "task.task_strategy.start_strategy", "schedule": 60.0, "args": ()},
        "get_new_candles": {"task": "task.task_get_new_candles.get_new_candles", "schedule": 900.0, "args": ()},
    }
register_dev_accounts.delay()

if LOAD_SECURITIES:
    sleep(5)
    get_new_candles.delay()
