import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from fastapi import APIRouter, Depends
from securities.schemas import SecurityOutSchema
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from starlette.responses import JSONResponse
from starlette.status import HTTP_204_NO_CONTENT
from strategies.upload_data import upload_data_from_files

from api.deps import get_historic_candles_service, get_security_service

router = APIRouter()
logger = logging.getLogger("api")

SecurityServiceDeps = Annotated[SecuritiesService, Depends(get_security_service)]
HistoricCandlesServiceDeps = Annotated[HistoricCandlesService, Depends(get_historic_candles_service)]
UserDeps = Annotated[User, Depends(current_active_user)]


@router.get("/", response_model=list[SecurityOutSchema])
async def get_all_securities(service: SecurityServiceDeps, user: UserDeps) -> list[SecurityOutSchema]:
    return await service.get_all_securities()


@router.post("/", response_model=list[SecurityOutSchema])
async def get_securities_by_tickers(
    tickers: list[str], include_historic_candles: bool, service: SecurityServiceDeps, user: UserDeps
) -> list[SecurityOutSchema]:
    return await service.get_securities_by_tickers(tickers, include_historic_candles)


@router.patch("/", status_code=HTTP_204_NO_CONTENT, responses={401: {"message": "string"}, 204: {}})
async def upload_securities_from_files(
    user: UserDeps, service: SecurityServiceDeps, historic_candles_service: HistoricCandlesServiceDeps
) -> JSONResponse:
    await upload_data_from_files(user, service, historic_candles_service)
    return JSONResponse(status_code=HTTP_204_NO_CONTENT, content=None)
