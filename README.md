# Real-Time Quant Trading Indicator System

Production-style full-stack signal platform with a strict `>=90%` confidence gate.

## Stack
- **Backend:** FastAPI + WebSocket + technical indicator pipeline.
- **ML:** Gradient Boosting inference (with fallback heuristic scorer).
- **Sentiment:** Financial RSS headline scoring.
- **Global Trend:** BTC higher-timeframe slope proxy.
- **Frontend:** Next.js dark dashboard + TradingView Lightweight Charts.
- **Ops:** Dockerfiles + docker-compose.

## Project Structure
- `backend/` API, signal engine, services, websocket stream, tests.
- `frontend/` Trading dashboard with chart, BUY/SELL labels, probability and sentiment/global trend panels.
- `model/` training and backtesting modules.
- `data_pipeline/` retraining pipeline orchestration.

## Backend setup
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
uvicorn app.main:app --reload --port 8000
```

## Frontend setup
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## API Endpoints
- `GET /health`
- `GET /signals/candles?symbol=BTCUSDT&interval=1m`
- `GET /signals/latest?symbol=BTCUSDT&interval=1m`
- `GET /signals/metrics`
- `WS /signals/stream?symbol=BTCUSDT&interval=1m`

## Signal Logic
1. Ingest live OHLCV from Binance.
2. Compute RSI, MACD, moving averages, volatility, volume spike, trap/exhaustion scores.
3. Pull market news headlines and derive sentiment score.
4. Compute global trend proxy.
5. Predict next-candle direction and confidence.
6. Emit `BUY`/`SELL` **only when confidence >= 0.90**, else `NO TRADE`.

## Training / Retraining
```bash
python model/train.py
python model/backtest.py
python data_pipeline/retrain_pipeline.py
```

## Risk Management and Tracking
- Context payload returns risk suggestion (1% max equity risk guideline).
- Accuracy tracker endpoint scaffolding provided for rolling signal performance.

## Docker
```bash
docker compose up --build
```

## Deployment Notes
- Add API keys (NewsAPI/Finnhub/AlphaVantage) via environment variables in production.
- Replace heuristic sentiment with provider sentiment endpoint for improved quality.
- Add persistent store (Postgres/Redis) for full accuracy/telemetry and retraining datasets.
