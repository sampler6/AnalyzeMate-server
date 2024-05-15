from typing import Optional

from pydantic import BaseModel
from tinkoff.invest import CandleInterval


class HistoricCandlesSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    ticker: str
    timeframe: CandleInterval
    timestamp: float


class HistoricCandlesOutSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    ticker: str
    timeframe: int
    timestamp: float


class SecurityShortOutSchema(BaseModel):
    ticker: str
    name: str
    price: Optional[float]


class SecurityWithVolumeAndPriceOutSchema(BaseModel):
    ticker: str
    name: str
    price: Optional[float]
    volume: Optional[int]
    delta_price: Optional[float]


class SecurityOutSchema(BaseModel):
    ticker: str
    name: str
    price: float
    historic_candles: Optional[list[HistoricCandlesOutSchema]]


supported_shares = {
    "TATN": "Татнефть",
    "ROSN": "Роснефть",
    "LKOH": "Лукойл",
    "GAZP": "Газпром",
    "SIBN": "Газпром нефть",
    "PIKK": "Пик",
    "SMLT": "ГК Самолет",
    "MAGN": "Магнитогорский металлургический комбинат",
    "NLMK": "НЛМК",
    "CHMF": "Северсталь",
    "SBER": "Сбер Банк",
    "VTBR": "Банк ВТБ",
    "TCSG": "ТКС Холдинг",
    "AQUA": "Инарктирка",
    "ABIO": "Артген",
    "MDMG": "Мать и дитя",
    "CBOM": "МОСКОВСКИЙ КРЕДИТНЫЙ БАНК",
    "ALRS": "АЛРОСА",
    "LENT": "Лента",
    "VKCO": "ВК",
    "RUAL": 'Объединённая Компания "РУСАЛ"',
    "AFKS": 'Акционерная финансовая корпорация "Система"',
    "AFLT": "Аэрофлот – российские авиалинии",
    "EUTR": "ЕвроТранс",
    "IRAO": "Интер РАО ЕЭС",
    "POSI": "Группа Позитив",
    "BELU": "НоваБев Групп",
    "PHOR": "ФосАгро",
    "PLZL": "Полюс",
    "RTKMP": "Ростелеком",
}
