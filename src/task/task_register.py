import asyncio
import time
from logging import getLogger

from auth import User
from celery import shared_task
from config import APP_PORT
from httpx import Client
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from task.base import engine

logger = getLogger("api")


@shared_task(default_retry_delay=2 * 5, max_retries=2)
def register_dev_accounts() -> None:
    time.sleep(5)
    data = {
        "birthdate": "2024-04-06T16:09:20.161173Z",
        "patronymic": "test",
        "surname": "client",
        "name": "aaa",
        "balance": 0,
        "config": {"test": "test"},
    }
    ids = []
    with Client(base_url=f"http://app:{APP_PORT}/") as client:
        response = client.post("auth/register", json=data | {"email": "admin@admin.ru", "password": "Admin123"})
        if response.status_code == 201:
            logger.info("Аккаунт администратора зарегистрирован")
            ids.append(response.json()["id"])

        response = client.post("auth/register", json=data | {"email": "test@example.com", "password": "Test12345"})
        if response.status_code == 201:
            logger.info("Аккаунт авто тестов зарегистрирован")
            ids.append(response.json()["id"])

        session = AsyncSession(engine)
        try:
            stmt = update(User).where(User.id.in_(ids)).values(is_superuser=True)
            asyncio.run(session.execute(stmt))
            asyncio.run(session.commit())
            logger.info("Права суперпользователя успешно выданы")
        except Exception:
            session.rollback()
            raise
        finally:
            asyncio.run(session.close())
