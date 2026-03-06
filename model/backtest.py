import asyncio
import pandas as pd

from app.services.market_data import market_data_service
from app.services.indicators import build_features
from app.services.model_inference import inference_engine


async def backtest(symbol: str = "BTCUSDT", interval: str = "1m", threshold: float = 0.9, lookback: int = 220):
    df = await market_data_service.fetch_ohlcv(symbol, interval, limit=lookback)
    trades, wins = 0, 0

    for i in range(60, len(df) - 1):
        sl = df.iloc[: i + 1]
        features = build_features(sl, news_sentiment=0.0, global_trend=0.0)
        direction, prob = inference_engine.predict_direction_probability(features)
        if prob < threshold:
            continue

        trades += 1
        next_ret = df["close"].iloc[i + 1] - df["close"].iloc[i]
        if (direction == "BUY" and next_ret > 0) or (direction == "SELL" and next_ret < 0):
            wins += 1

    acc = wins / trades if trades else 0
    print({"trades": trades, "wins": wins, "accuracy": acc})


if __name__ == "__main__":
    asyncio.run(backtest())
