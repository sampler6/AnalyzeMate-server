import logging
from logging import getLogger

from api.api import router as api_router
from exceptions.base import exception_traceback_middleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

origins = [
    "*",
]

logger = getLogger("api")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

app = FastAPI(
    Title="AnalyzeMate-server",
)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(exception_traceback_middleware)

app.include_router(api_router)
