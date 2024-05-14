import functools
from datetime import datetime, timedelta
from typing import Any


def check_time(milliseconds: int = 300) -> Any:
    """Проверка времени выполнения тестов"""

    def decorator(function: Any) -> Any:
        @functools.wraps(function)
        async def wrapper(*args, **kwargs) -> Any:  # type: ignore
            start = datetime.now()
            result = await function(*args, **kwargs)
            delta_time = datetime.now() - start

            assert delta_time <= timedelta(milliseconds=milliseconds), (
                f"The request time is more than: {milliseconds}ms. "
                f"Actual time is {delta_time.seconds * 1000 + delta_time.microseconds/1000}ms"
            )

            return result

        return wrapper

    return decorator
