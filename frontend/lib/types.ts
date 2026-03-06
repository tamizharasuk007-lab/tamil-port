export type Candle = {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export type StreamPayload = {
  signal: null | {
    symbol: string
    interval: string
    timestamp: string
    signal: 'BUY' | 'SELL'
    probability: number
    sentiment: number
    global_trend: number
    reason: string
  }
  context: {
    signal: string
    probability: number
    sentiment: number
    global_trend: number
  }
}
