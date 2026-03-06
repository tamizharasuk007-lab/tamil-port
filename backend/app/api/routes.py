from __future__ import annotations

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.models.schemas import AccuracyPoint
from app.services.signal_engine import SignalEngine

router = APIRouter()
engine = SignalEngine()


@router.get('/health')
def health():
    return {'status': 'ok'}


@router.get('/signal')
async def get_signal(symbol: str = 'BTC-USD', timeframe: str = '1m'):
    payload = await engine.analyze(symbol, timeframe)
    return payload.model_dump(mode='json')


@router.get('/accuracy')
def get_accuracy():
    return {'rolling_accuracy': engine.tracker.accuracy(), 'samples': len(engine.tracker.points)}


@router.websocket('/ws/signals')
async def websocket_signals(websocket: WebSocket, symbol: str = 'BTC-USD', timeframe: str = '1m'):
    await websocket.accept()
    last_prediction = None
    try:
        while True:
            payload = await engine.analyze(symbol, timeframe)
            await websocket.send_json(payload.model_dump(mode='json'))

            if last_prediction is not None and last_prediction['signal'] in {'BUY', 'SELL'}:
                actual = 'BUY' if payload.candle.close > last_prediction['close'] else 'SELL'
                engine.tracker.record(
                    AccuracyPoint(
                        timestamp=payload.candle.time,
                        predicted=last_prediction['signal'],
                        actual=actual,
                        is_correct=(last_prediction['signal'] == actual),
                    )
                )

            last_prediction = {'signal': payload.signal, 'close': payload.candle.close}
            await asyncio.sleep(settings.polling_interval_seconds)
    except WebSocketDisconnect:
        return
