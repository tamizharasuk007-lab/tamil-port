import pytest

from app.config import settings
from app.services.model_inference import inference_engine


def test_threshold_constant():
    assert settings.prediction_threshold == pytest.approx(0.90)


def test_prediction_bounds():
    direction, prob = inference_engine.predict_direction_probability(
        {
            "rsi": 62,
            "macd": 0.2,
            "macd_signal": 0.1,
            "ma_fast": 101,
            "ma_slow": 100,
            "volume_spike": 1.3,
            "volatility": 0.02,
            "trend_strength": 0.01,
            "trap_score": 0.1,
            "exhaustion_score": 0.2,
            "news_sentiment": 0.3,
            "global_trend": 0.2,
        }
    )
    assert direction in {"BUY", "SELL"}
    assert 0 <= prob <= 1
