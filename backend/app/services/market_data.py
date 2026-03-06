from datetime import datetime
import httpx
import pandas as pd

from app.config import settings


class MarketDataService:
    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int = 250) -> pd.DataFrame:
        url = f"{settings.binance_base_url}/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        try:
            async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
            raw = response.json()

            df = pd.DataFrame(
                raw,
                columns=[
                    "open_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "qav",
                    "trades",
                    "tbbav",
                    "tbqav",
                    "ignore",
                ],
            )
            num_cols = ["open", "high", "low", "close", "volume"]
            df[num_cols] = df[num_cols].astype(float)
            df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
            return df[["timestamp", *num_cols]]
        except Exception:
            return self._synthetic_ohlcv(limit)

    def _synthetic_ohlcv(self, limit: int) -> pd.DataFrame:
        import numpy as np

        rng = np.random.default_rng(42)
        base = 60000 + np.cumsum(rng.normal(0, 40, limit))
        close = base + rng.normal(0, 10, limit)
        open_ = base
        high = np.maximum(open_, close) + rng.uniform(5, 25, limit)
        low = np.minimum(open_, close) - rng.uniform(5, 25, limit)
        volume = np.abs(rng.normal(1500, 280, limit))
        ts = pd.date_range(end=datetime.utcnow(), periods=limit, freq="min")
        return pd.DataFrame({"timestamp": ts, "open": open_, "high": high, "low": low, "close": close, "volume": volume})

    async def fetch_global_trend(self) -> float:
        df = await self.fetch_ohlcv("BTCUSDT", "1h", limit=72)
        slope = (df["close"].iloc[-1] - df["close"].iloc[-24]) / df["close"].iloc[-24]
        return float(max(min(slope * 8, 1), -1))


market_data_service = MarketDataService()
