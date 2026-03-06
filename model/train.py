from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

from app.services.indicators import build_features


def synth_data(n: int = 1000):
    rng = np.random.default_rng(7)
    rows = []
    for _ in range(n):
        price = 100 + np.cumsum(rng.normal(0, 0.5, 300))
        volume = np.abs(rng.normal(1000, 200, 300))
        df = pd.DataFrame({
            "timestamp": pd.date_range("2023-01-01", periods=300, freq="min"),
            "open": price,
            "high": price + rng.uniform(0, 0.7, 300),
            "low": price - rng.uniform(0, 0.7, 300),
            "close": price + rng.normal(0, 0.2, 300),
            "volume": volume,
        })
        news = float(rng.uniform(-1, 1))
        global_t = float(rng.uniform(-1, 1))
        feats = build_features(df, news, global_t)
        y = int((df["close"].iloc[-1] - df["close"].iloc[-2]) > 0)
        rows.append((feats, y))
    return rows


def main():
    rows = synth_data()
    X = pd.DataFrame([r[0] for r in rows])
    y = np.array([r[1] for r in rows])

    clf = GradientBoostingClassifier(random_state=42)
    clf.fit(X.values, y)

    out = Path("model/artifacts")
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, out / "gb_model.pkl")
    print("saved", out / "gb_model.pkl")


if __name__ == "__main__":
    main()
