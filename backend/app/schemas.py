from datetime import datetime
from pydantic import BaseModel


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Features(BaseModel):
    rsi: float
    macd: float
    macd_signal: float
    ma_fast: float
    ma_slow: float
    volatility: float
    volume_spike: float
    trend_strength: float
    trap_score: float
    exhaustion_score: float
    news_sentiment: float
    global_trend: float


class Prediction(BaseModel):
    direction: str
    probability: float
    confidence: float


class Signal(BaseModel):
    symbol: str
    interval: str
    timestamp: datetime
    signal: str
    probability: float
    sentiment: float
    global_trend: float
    reason: str
