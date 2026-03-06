import numpy as np
import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    line = ema_fast - ema_slow
    signal_line = line.ewm(span=signal, adjust=False).mean()
    return line, signal_line


def build_features(df: pd.DataFrame, news_sentiment: float, global_trend: float) -> dict[str, float]:
    close = df["close"]
    volume = df["volume"]
    ma_fast = close.rolling(9).mean().iloc[-1]
    ma_slow = close.rolling(21).mean().iloc[-1]
    macd_line, macd_signal = macd(close)
    rolling_ret = close.pct_change().rolling(20)

    trend_strength = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) if len(close) > 10 else 0
    wick_ratio = ((df["high"].iloc[-1] - df["close"].iloc[-1]) + (df["open"].iloc[-1] - df["low"].iloc[-1])) / max(
        abs(df["close"].iloc[-1] - df["open"].iloc[-1]), 1e-8
    )

    return {
        "rsi": float(rsi(close).iloc[-1]),
        "macd": float(macd_line.iloc[-1]),
        "macd_signal": float(macd_signal.iloc[-1]),
        "ma_fast": float(ma_fast),
        "ma_slow": float(ma_slow),
        "volatility": float(rolling_ret.std().iloc[-1] if not np.isnan(rolling_ret.std().iloc[-1]) else 0),
        "volume_spike": float(volume.iloc[-1] / max(volume.rolling(20).mean().iloc[-1], 1e-8)),
        "trend_strength": float(trend_strength),
        "trap_score": float(max(min(wick_ratio / 4, 1), 0)),
        "exhaustion_score": float(max(min(abs(trend_strength) * 8 + abs((rsi(close).iloc[-1] - 50) / 50), 1), 0)),
        "news_sentiment": float(news_sentiment),
        "global_trend": float(global_trend),
    }
