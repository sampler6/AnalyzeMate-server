from api.api import router as api_router
from exceptions.base import exception_traceback_middleware
from fastapi import FastAPI
from fastapi.security import HTTPBearer

app = FastAPI(
    Title="AnalyzeMate-server",
    swagger_ui_init_oauth={
        "securityDefinitions": {
            "Bearer": {
                "name": "AuthorizationBearer",
                "in": "header",
                "type": "apiKey",
                "description": "HTTP/HTTPS Bearer",
            }
        }
    },
)

app.middleware("http")(exception_traceback_middleware)

app.include_router(api_router)

auth_schema = HTTPBearer()
