from celery.app import Celery
from config import REDIS_HOST

from task.task_upload import upload_data_from_files

app_celery = Celery(
    "task",
    broker=f"redis://{REDIS_HOST}:6379",
    backend=f"redis://{REDIS_HOST}:6379",
    broker_connection_retry_on_startup=True,
)

upload_data_from_files.delay()
