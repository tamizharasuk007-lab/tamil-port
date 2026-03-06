from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from app.services.data_provider import MarketDataProvider
from app.services.ml import MLService
from app.services.technical import add_indicators


def train(symbol: str = 'BTC-USD', timeframe: str = '5m') -> Path:
    provider = MarketDataProvider()
    frame = provider.fetch_ohlcv(symbol, timeframe, limit=1000)
    enriched = add_indicators(frame)
    enriched['news_sentiment'] = 0.0
    enriched['global_trend'] = 0.0
    ml = MLService(model_path=ROOT / 'model' / 'gradient_boosting.pkl')
    ml.ensure_model(enriched)
    return ml.model_path


if __name__ == '__main__':
    path = train()
    print(f'Model saved to {path}')
