from __future__ import annotations

from pathlib import Path
import joblib
import numpy as np

FEATURE_ORDER = [
    "rsi",
    "macd",
    "macd_signal",
    "ma_fast",
    "ma_slow",
    "volume_spike",
    "volatility",
    "trend_strength",
    "trap_score",
    "exhaustion_score",
    "news_sentiment",
    "global_trend",
]


class InferenceEngine:
    def __init__(self) -> None:
        self.model = None
        model_path = Path("model/artifacts/gb_model.pkl")
        if model_path.exists():
            self.model = joblib.load(model_path)

    def predict_direction_probability(self, features: dict[str, float]) -> tuple[str, float]:
        x = np.array([[features[k] for k in FEATURE_ORDER]], dtype=float)

        if self.model is not None:
            up_prob = float(self.model.predict_proba(x)[0, 1])
        else:
            up_prob = self._heuristic_probability(features)

        direction = "BUY" if up_prob >= 0.5 else "SELL"
        probability = up_prob if direction == "BUY" else (1 - up_prob)
        return direction, float(probability)

    def _heuristic_probability(self, f: dict[str, float]) -> float:
        momentum = 0.25 * np.tanh(f["trend_strength"] * 20)
        macd_factor = 0.2 * np.tanh((f["macd"] - f["macd_signal"]) * 4)
        rsi_factor = 0.15 * ((f["rsi"] - 50) / 50)
        volume_confirm = 0.1 * np.tanh((f["volume_spike"] - 1) * 2)
        context = 0.15 * f["news_sentiment"] + 0.1 * f["global_trend"]
        trap_penalty = -0.15 * f["trap_score"]
        exhaustion_penalty = -0.08 * f["exhaustion_score"]

        logit = momentum + macd_factor + rsi_factor + volume_confirm + context + trap_penalty + exhaustion_penalty
        return float(1 / (1 + np.exp(-logit * 3)))


inference_engine = InferenceEngine()
