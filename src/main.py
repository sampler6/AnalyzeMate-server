from api.api import router as api_router
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

app.include_router(api_router)

auth_schema = HTTPBearer()
