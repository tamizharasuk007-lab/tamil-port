from datetime import datetime

from app.config import settings
from app.schemas import Signal
from app.services.indicators import build_features
from app.services.market_data import market_data_service
from app.services.model_inference import inference_engine
from app.services.sentiment import sentiment_service


class SignalEngine:
    async def generate_signal(self, symbol: str, interval: str) -> tuple[Signal | None, dict]:
        ohlcv = await market_data_service.fetch_ohlcv(symbol, interval)
        news_sentiment = await sentiment_service.score_market_sentiment()
        global_trend = await market_data_service.fetch_global_trend()

        features = build_features(ohlcv, news_sentiment, global_trend)
        direction, probability = inference_engine.predict_direction_probability(features)

        risk = "Max 1% equity risk, stop-loss at 1.5x recent volatility."

        if probability < settings.prediction_threshold:
            return None, {
                "signal": "NO TRADE",
                "probability": probability,
                "sentiment": news_sentiment,
                "global_trend": global_trend,
                "features": features,
                "risk": risk,
            }

        signal = Signal(
            symbol=symbol,
            interval=interval,
            timestamp=datetime.utcnow(),
            signal=direction,
            probability=probability,
            sentiment=news_sentiment,
            global_trend=global_trend,
            reason="High-confidence momentum + context alignment",
        )
        return signal, {"features": features, "risk": risk}


signal_engine = SignalEngine()
