from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import pandas as pd

from app.core.config import settings
from app.models.schemas import AccuracyPoint, Candle, SignalPayload
from app.services.data_provider import MarketDataProvider
from app.services.ml import MLService
from app.services.news_sentiment import NewsSentimentService
from app.services.technical import add_indicators


@dataclass
class AccuracyTracker:
    points: deque[AccuracyPoint] = field(default_factory=lambda: deque(maxlen=2000))

    def record(self, point: AccuracyPoint) -> None:
        self.points.append(point)

    def accuracy(self) -> float:
        if not self.points:
            return 0.0
        return sum(1 for p in self.points if p.is_correct) / len(self.points)


@dataclass
class SignalEngine:
    provider: MarketDataProvider = field(default_factory=MarketDataProvider)
    sentiment: NewsSentimentService = field(default_factory=NewsSentimentService)
    ml: MLService = field(default_factory=MLService)
    tracker: AccuracyTracker = field(default_factory=AccuracyTracker)

    async def analyze(self, symbol: str, timeframe: str) -> SignalPayload:
        frame = self.provider.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
        news_score = await self.sentiment.score(symbol)
        global_trend = self.provider.fetch_global_trend()

        enriched = add_indicators(frame)
        enriched["news_sentiment"] = news_score
        enriched["global_trend"] = global_trend

        self.ml.ensure_model(enriched)
        latest = enriched.dropna().tail(1)
        if latest.empty:
            raise ValueError("Insufficient features for inference")

        bullish_prob = self.ml.predict_probability(latest)
        bearish_prob = 1.0 - bullish_prob

        direction = "BUY" if bullish_prob >= bearish_prob else "SELL"
        probability = bullish_prob if direction == "BUY" else bearish_prob
        signal = direction if probability >= settings.signal_probability_threshold else "NO TRADE"

        candle_row = frame.tail(1).iloc[0]
        indicators = {
            "rsi": float(latest["rsi"].iloc[0]),
            "macd": float(latest["macd"].iloc[0]),
            "momentum": float(latest["momentum"].iloc[0]),
            "trend_strength": float(latest["trend_strength"].iloc[0]),
            "fake_breakout_risk": float(latest["breakout_fake"].iloc[0]),
            "volatility": float(latest["volatility"].iloc[0]),
        }

        risk_note = self._risk_note(probability, indicators["volatility"])
        return SignalPayload(
            symbol=symbol,
            timeframe=timeframe,
            signal=signal,
            probability=probability,
            sentiment=news_score,
            global_trend=global_trend,
            risk_note=risk_note,
            candle=Candle(
                time=pd.to_datetime(candle_row["time"]).to_pydatetime(),
                open=float(candle_row["open"]),
                high=float(candle_row["high"]),
                low=float(candle_row["low"]),
                close=float(candle_row["close"]),
                volume=float(candle_row["volume"]),
            ),
            indicators=indicators,
        )

    @staticmethod
    def _risk_note(prob: float, volatility: float) -> str:
        if prob < 0.9:
            return "NO TRADE: confidence below 90%."
        if volatility > 0.02:
            return "High volatility: use reduced position size (e.g. <=0.5R)."
        return "Standard risk budget acceptable (e.g. 1R with stop below/above last swing)."
