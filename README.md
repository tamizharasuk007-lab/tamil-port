# Real-Time Quant Trading Indicator System

Production-oriented full-stack system that combines technical indicators, ML inference, news sentiment, and global index trend correlation to issue **BUY/SELL only when confidence >= 90%**, otherwise **NO TRADE**.

## Architecture

- **Frontend:** Next.js + lightweight-charts (TradingView-like dark UI)
- **Backend:** FastAPI + WebSocket real-time signal stream
- **Model:** Gradient Boosting classifier on engineered OHLCV + sentiment + global trend features
- **Pipelines:** Backtesting + retraining scripts

## Features implemented

- Real-time OHLCV ingestion (`yfinance`, pluggable provider)
- Technical features: RSI, MACD, moving averages, momentum, volatility, volume spikes, fake breakout heuristic
- News sentiment integration via NewsAPI (optional key)
- Global trend via US indices momentum (^GSPC, ^IXIC, ^DJI)
- ML probability inference for next candle direction
- 90% confidence filter (`NO TRADE` below threshold)
- WebSocket push updates for chart markers
- Risk note generation
- Rolling signal accuracy tracking
- Backtesting script and retraining pipeline

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/ws/signals npm run dev
```

Open: `http://localhost:3000`

## Docker

```bash
docker compose up --build
```

## API

- `GET /api/health`
- `GET /api/signal?symbol=BTC-USD&timeframe=1m`
- `GET /api/accuracy`
- `WS /api/ws/signals?symbol=BTC-USD&timeframe=1m`

## Retraining and backtest

```bash
python model/train.py
python model/backtest.py
python data_pipeline/retrain_pipeline.py --symbol BTC-USD --timeframe 5m
```

## Notes

- For production, swap `yfinance` with Binance/Polygon feed handlers and managed queue workers.
- Configure `NEWS_API_KEY` for live sentiment.
- Confidence threshold controlled by `SIGNAL_PROBABILITY_THRESHOLD` env variable (default `0.9`).
