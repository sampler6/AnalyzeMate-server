import logging

from notification.manager import manager

from task.base import redis_sync
from task.task import app_celery

logger = logging.getLogger("api")


@app_celery.task(default_retry_delay=2 * 5, max_retries=2)
def send_notification(user_ids: list[int], title: str, body: str) -> None:
    registrations_tokens = []
    for user in user_ids:
        if result := redis_sync.get(str(user) + "_token"):
            registrations_tokens.append(result.decode())

    logger.info("%s %s %s", registrations_tokens, title, body)
    manager.send_notifications(registrations_tokens, title, body)
