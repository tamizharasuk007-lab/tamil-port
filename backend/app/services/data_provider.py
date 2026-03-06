from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import yfinance as yf

_INTERVAL_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "60m",
}

_PERIOD_MAP = {
    "1m": "1d",
    "5m": "5d",
    "15m": "10d",
    "1h": "60d",
}


@dataclass
class MarketDataProvider:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 300) -> pd.DataFrame:
        interval = _INTERVAL_MAP.get(timeframe, "1m")
        period = _PERIOD_MAP.get(timeframe, "5d")
        try:
            ticker = yf.Ticker(symbol)
            raw = ticker.history(period=period, interval=interval)
            if raw.empty:
                raise ValueError("empty")

            raw = raw.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            data = raw[["open", "high", "low", "close", "volume"]].tail(limit).copy()
            data.index = pd.to_datetime(data.index).tz_convert(timezone.utc) if data.index.tz else pd.to_datetime(data.index, utc=True)
            data["time"] = data.index
            return data.reset_index(drop=True)
        except Exception:
            return self._synthetic_ohlcv(limit=limit, timeframe=timeframe)

    def fetch_global_trend(self) -> float:
        indices = ["^GSPC", "^IXIC", "^DJI"]
        momentum_scores = []
        for idx in indices:
            try:
                data = yf.Ticker(idx).history(period="5d", interval="1h")
                if len(data) < 5:
                    continue
                close = data["Close"]
                momentum_scores.append(float((close.iloc[-1] - close.iloc[-5]) / (close.iloc[-5] + 1e-9)))
            except Exception:
                continue
        if not momentum_scores:
            return 0.0
        return float(sum(momentum_scores) / len(momentum_scores))

    def _synthetic_ohlcv(self, limit: int, timeframe: str) -> pd.DataFrame:
        step_minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}.get(timeframe, 1)
        end = datetime.now(timezone.utc)
        times = [end - timedelta(minutes=step_minutes * i) for i in reversed(range(limit))]
        walk = np.cumsum(np.random.normal(0, 0.2, limit)) + 100
        close = pd.Series(walk)
        open_ = close.shift(1).fillna(close.iloc[0])
        high = pd.concat([open_, close], axis=1).max(axis=1) + np.random.rand(limit) * 0.2
        low = pd.concat([open_, close], axis=1).min(axis=1) - np.random.rand(limit) * 0.2
        volume = np.random.randint(100, 1000, size=limit)
        return pd.DataFrame({"time": times, "open": open_, "high": high, "low": low, "close": close, "volume": volume})

    @staticmethod
    def utc_now() -> datetime:
        return datetime.now(timezone.utc)
