import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from app.services.signal_engine import SignalEngine


async def run_backtest(symbol: str = 'BTC-USD', timeframe: str = '5m', steps: int = 20):
    engine = SignalEngine()
    wins = 0
    trades = 0
    last = None

    for _ in range(steps):
        payload = await engine.analyze(symbol, timeframe)
        if last and last['signal'] in {'BUY', 'SELL'}:
            actual = 'BUY' if payload.candle.close > last['close'] else 'SELL'
            wins += int(actual == last['signal'])
            trades += 1
        last = {'signal': payload.signal, 'close': payload.candle.close}

    print({'trades': trades, 'wins': wins, 'win_rate': wins / trades if trades else 0.0})


if __name__ == '__main__':
    asyncio.run(run_backtest())
