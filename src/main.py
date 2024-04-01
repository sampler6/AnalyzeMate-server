from api.api import router as api_router
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:8000",
]


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

app.include_router(api_router)
