from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "rsi",
    "macd",
    "macd_hist",
    "ma_fast",
    "ma_slow",
    "volume_spike",
    "volatility",
    "trend_strength",
    "momentum",
    "breakout_fake",
    "news_sentiment",
    "global_trend",
]


@dataclass
class MLService:
    model_path: Path = Path("model/gradient_boosting.pkl")
    pipeline: Pipeline | None = field(default=None)

    def __post_init__(self) -> None:
        if self.model_path.exists():
            self.pipeline = joblib.load(self.model_path)

    def ensure_model(self, frame: pd.DataFrame) -> None:
        if self.pipeline is not None:
            return
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", GradientBoostingClassifier(random_state=42, n_estimators=150)),
            ]
        )
        train = frame.dropna().copy()
        train["target"] = (train["close"].shift(-1) > train["close"]).astype(int)
        train = train.dropna()
        if len(train) < 80:
            raise ValueError("Not enough samples to train model")
        x_train = train[FEATURES]
        y_train = train["target"]
        self.pipeline.fit(x_train, y_train)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)

    def predict_probability(self, latest_features: pd.DataFrame) -> float:
        if self.pipeline is None:
            raise RuntimeError("Model not initialized")
        probs = self.pipeline.predict_proba(latest_features[FEATURES])
        return float(probs[0][1])
