from api.api import router as api_router
from fastapi import FastAPI

app = FastAPI(Title="AnalyzeMate-server")

app.include_router(api_router)
