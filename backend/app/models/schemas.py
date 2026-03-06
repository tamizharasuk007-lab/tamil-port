from datetime import datetime
from pydantic import BaseModel


class Candle(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class SignalPayload(BaseModel):
    symbol: str
    timeframe: str
    signal: str
    probability: float
    sentiment: float
    global_trend: float
    risk_note: str
    candle: Candle
    indicators: dict


class AccuracyPoint(BaseModel):
    timestamp: datetime
    predicted: str
    actual: str
    is_correct: bool
