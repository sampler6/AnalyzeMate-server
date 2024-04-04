from logging import getLogger
from typing import Any, Callable

from fastapi.requests import Request
from starlette import status
from starlette.responses import JSONResponse, Response

logger = getLogger("api")


async def exception_traceback_middleware(request: Request, call_next: Callable) -> Response:
    try:
        response: Response = await call_next(request)
    except ValidationException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": e.message},
        )
    except ResourceNotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": e.message},
        )
    except ConflictingStateException as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": e.message},
        )
    except AccessDeniedException as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": e.message},
        )
    except Exception as e:
        logger.exception("%s: %s", e.__class__.__name__, e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={})
    else:
        return response


class BaseExceptionWithMessage(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundException(BaseExceptionWithMessage):
    template: str

    def __init__(self, template: str = "Not found", **kwargs: Any):
        self.template = template
        self._kw = kwargs
        self.message = self.__str__()
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.template.format(**self._kw)


class ValidationException(BaseExceptionWithMessage):
    pass


class ConflictingStateException(BaseExceptionWithMessage):
    pass


class AccessDeniedException(BaseExceptionWithMessage):
    pass
