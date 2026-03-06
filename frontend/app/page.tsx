'use client'

import { useEffect, useMemo, useState } from 'react'
import TradingChart, { Marker } from '../components/TradingChart'
import type { Candle, StreamPayload } from '../lib/types'

const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export default function Page() {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [interval, setInterval] = useState('1m')
  const [candles, setCandles] = useState<Candle[]>([])
  const [feed, setFeed] = useState<StreamPayload | null>(null)
  const [signalHistory, setSignalHistory] = useState<{ time: number; side: 'BUY' | 'SELL' }[]>([])

  useEffect(() => {
    fetch(`${API}/signals/candles?symbol=${symbol}&interval=${interval}`)
      .then((r) => r.json())
      .then((d: Candle[]) => setCandles(d))
  }, [symbol, interval])

  useEffect(() => {
    const ws = new WebSocket(`${API.replace('http', 'ws')}/signals/stream?symbol=${symbol}&interval=${interval}`)
    ws.onmessage = (ev) => {
      const payload: StreamPayload = JSON.parse(ev.data)
      setFeed(payload)
      if (payload.signal) {
        setSignalHistory((prev) => [
          ...prev,
          { time: Math.floor(new Date(payload.signal!.timestamp).getTime() / 1000), side: payload.signal!.signal }
        ].slice(-40))
      }
    }
    return () => ws.close()
  }, [symbol, interval])

  const markers = useMemo<Marker[]>(
    () =>
      signalHistory.map((s) => ({
        time: s.time,
        position: s.side === 'BUY' ? 'belowBar' : 'aboveBar',
        color: s.side === 'BUY' ? '#0fa968' : '#db3f57',
        shape: s.side === 'BUY' ? 'arrowUp' : 'arrowDown',
        text: s.side
      })),
    [signalHistory]
  )

  return (
    <main style={{ padding: 16 }}>
      <h2>AI Quant Signal Dashboard (≥90% confidence filter)</h2>
      <div className="controls">
        <div className="panel">
          Asset{' '}
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
            <option>BTCUSDT</option>
            <option>ETHUSDT</option>
            <option>BNBUSDT</option>
          </select>
        </div>
        <div className="panel">
          Timeframe{' '}
          <select value={interval} onChange={(e) => setInterval(e.target.value)}>
            <option>1m</option>
            <option>5m</option>
            <option>15m</option>
          </select>
        </div>
      </div>

      <div className="grid">
        <TradingChart candles={candles} markers={markers} />
        <div className="panel">
          <h3>Signal Engine</h3>
          <p>
            Current: {feed?.signal ? <span className={feed.signal.signal === 'BUY' ? 'label-buy' : 'label-sell'}>{feed.signal.signal}</span> : 'NO TRADE'}
          </p>
          <p>Probability: {((feed?.signal?.probability ?? feed?.context?.probability ?? 0) * 100).toFixed(2)}%</p>
          <p>Market Sentiment: {((feed?.signal?.sentiment ?? feed?.context?.sentiment ?? 0) * 100).toFixed(1)}%</p>
          <p>Global Trend: {((feed?.signal?.global_trend ?? feed?.context?.global_trend ?? 0) * 100).toFixed(1)}%</p>
          <p>Filter: Signals shown only when probability ≥ 90%.</p>
        </div>
      </div>
    </main>
  )
}
