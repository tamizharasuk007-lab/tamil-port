'use client'

import { createChart, IChartApi, ISeriesApi, CandlestickData } from 'lightweight-charts'
import { useEffect, useRef } from 'react'
import type { Candle } from '../lib/types'

export type Marker = { time: number; position: 'aboveBar' | 'belowBar'; color: string; shape: 'arrowUp' | 'arrowDown'; text: string }

export default function TradingChart({ candles, markers }: { candles: Candle[]; markers: Marker[] }) {
  const ref = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

  useEffect(() => {
    if (!ref.current) return
    const chart = createChart(ref.current, {
      layout: { background: { color: '#141a26' }, textColor: '#d7deee' },
      grid: { vertLines: { color: '#1f2737' }, horzLines: { color: '#1f2737' } },
      width: ref.current.clientWidth,
      height: 460
    })
    const series = chart.addCandlestickSeries({
      upColor: '#2ac38d',
      downColor: '#db3f57',
      wickUpColor: '#2ac38d',
      wickDownColor: '#db3f57',
      borderVisible: false
    })
    chartRef.current = chart
    seriesRef.current = series

    const resize = () => chart.applyOptions({ width: ref.current?.clientWidth || 900 })
    window.addEventListener('resize', resize)
    return () => {
      window.removeEventListener('resize', resize)
      chart.remove()
    }
  }, [])

  useEffect(() => {
    if (!seriesRef.current) return
    const formatted: CandlestickData[] = candles.map((c) => ({
      time: Math.floor(new Date(c.timestamp).getTime() / 1000) as CandlestickData['time'],
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close
    }))
    seriesRef.current.setData(formatted)
    seriesRef.current.setMarkers(markers as never)
  }, [candles, markers])

  return <div className="panel" ref={ref} />
}
