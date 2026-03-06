import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.services.signal_engine import signal_engine

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/candles")
async def candles(symbol: str = settings.default_symbol, interval: str = settings.default_interval, limit: int = 200):
    from app.services.market_data import market_data_service
    df = await market_data_service.fetch_ohlcv(symbol, interval, limit=limit)
    return df.to_dict(orient="records")


@router.get("/latest")
async def latest(symbol: str = settings.default_symbol, interval: str = settings.default_interval):
    signal, context = await signal_engine.generate_signal(symbol, interval)
    return {"signal": signal.model_dump() if signal else None, "context": context}


@router.websocket("/stream")
async def stream(websocket: WebSocket, symbol: str = settings.default_symbol, interval: str = settings.default_interval):
    await websocket.accept()
    try:
        while True:
            signal, context = await signal_engine.generate_signal(symbol, interval)
            payload = {"signal": signal.model_dump() if signal else None, "context": context}
            await websocket.send_json(payload)
            await asyncio.sleep(settings.ws_interval_seconds)
    except WebSocketDisconnect:
        return

@router.get("/metrics")
async def metrics():
    from app.services.metrics import accuracy_tracker
    return {"rolling_accuracy": accuracy_tracker.accuracy}

