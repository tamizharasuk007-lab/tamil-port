import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws/signals';

export default function TradingDashboard() {
  const chartRef = useRef(null);
  const candleSeries = useRef(null);
  const chart = useRef(null);
  const [symbol, setSymbol] = useState('BTC-USD');
  const [timeframe, setTimeframe] = useState('1m');
  const [payload, setPayload] = useState(null);

  useEffect(() => {
    chart.current = createChart(chartRef.current, {
      layout: { background: { type: ColorType.Solid, color: '#0f1420' }, textColor: '#d1d4dc' },
      grid: { vertLines: { color: '#222' }, horzLines: { color: '#222' } },
      width: chartRef.current.clientWidth,
      height: 500,
      rightPriceScale: { borderColor: '#2B2B43' },
      timeScale: { borderColor: '#2B2B43' },
    });

    candleSeries.current = chart.current.addCandlestickSeries({
      upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
      wickUpColor: '#26a69a', wickDownColor: '#ef5350',
    });

    const resize = () => chart.current.applyOptions({ width: chartRef.current.clientWidth });
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
      chart.current.remove();
    };
  }, []);

  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}?symbol=${encodeURIComponent(symbol)}&timeframe=${timeframe}`);
    const markers = [];

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPayload(data);
      const c = data.candle;
      candleSeries.current.update({
        time: Math.floor(new Date(c.time).getTime() / 1000),
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      });
      if (data.signal === 'BUY' || data.signal === 'SELL') {
        markers.push({
          time: Math.floor(new Date(c.time).getTime() / 1000),
          position: data.signal === 'BUY' ? 'belowBar' : 'aboveBar',
          color: data.signal === 'BUY' ? '#00c853' : '#ff1744',
          shape: data.signal === 'BUY' ? 'arrowUp' : 'arrowDown',
          text: `${data.signal} ${(data.probability * 100).toFixed(1)}%`,
        });
        candleSeries.current.setMarkers(markers);
      }
    };

    return () => ws.close();
  }, [symbol, timeframe]);

  return (
    <div className="container">
      <div className="toolbar">
        <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
          <option>BTC-USD</option>
          <option>ETH-USD</option>
          <option>AAPL</option>
          <option>TSLA</option>
        </select>
        <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
          <option value="1m">1m</option>
          <option value="5m">5m</option>
          <option value="15m">15m</option>
          <option value="1h">1h</option>
        </select>
      </div>

      <div ref={chartRef} className="chart" />

      <div className="stats">
        <div><strong>Signal:</strong> {payload?.signal || 'NO TRADE'}</div>
        <div><strong>Probability:</strong> {payload ? `${(payload.probability * 100).toFixed(2)}%` : '--'}</div>
        <div><strong>Market Sentiment:</strong> {payload ? payload.sentiment.toFixed(3) : '--'}</div>
        <div><strong>Global Trend:</strong> {payload ? payload.global_trend.toFixed(3) : '--'}</div>
        <div><strong>Risk:</strong> {payload?.risk_note || '--'}</div>
      </div>
    </div>
  );
}
