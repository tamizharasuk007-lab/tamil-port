import pandas as pd

from app.services.technical import add_indicators


def test_add_indicators_generates_columns():
    df = pd.DataFrame(
        {
            'open': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            'high': [2] * 21,
            'low': [1] * 21,
            'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            'volume': [100] * 21,
        }
    )
    out = add_indicators(df)
    assert {'rsi', 'macd', 'ma_fast', 'ma_slow', 'volatility', 'volume_spike'}.issubset(out.columns)
