from __future__ import annotations

import numpy as np
import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    gain_ema = pd.Series(gain, index=series.index).ewm(alpha=1 / period, adjust=False).mean()
    loss_ema = pd.Series(loss, index=series.index).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain_ema / (loss_ema + 1e-9)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["rsi"] = rsi(data["close"])
    macd_line, signal_line, hist = macd(data["close"])
    data["macd"] = macd_line
    data["macd_signal"] = signal_line
    data["macd_hist"] = hist
    data["ma_fast"] = data["close"].rolling(9).mean()
    data["ma_slow"] = data["close"].rolling(21).mean()
    data["volatility"] = data["close"].pct_change().rolling(20).std()
    data["volume_spike"] = data["volume"] / (data["volume"].rolling(20).mean() + 1e-9)
    data["trend_strength"] = (data["ma_fast"] - data["ma_slow"]) / (data["close"] + 1e-9)
    data["momentum"] = data["close"].pct_change(3)
    data["breakout_fake"] = ((data["high"] - data["close"]) > (data["close"] - data["low"])) * 1.0
    return data
