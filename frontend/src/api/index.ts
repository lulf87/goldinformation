import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export type MarketState = 'trend' | 'range' | 'unclear'
export type SignalLevel = 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
export type PositionLevel = 'low' | 'medium' | 'high'

export interface TechnicalIndicators {
  ma_short?: number
  ma_mid?: number
  trend_dir?: string
  trend_strength?: string
  support_level?: number
  resistance_level?: number
  range_high?: number
  range_low?: number
  range_mid?: number
  atr?: number
  vol_state?: string
}

export interface TradingSignal {
  signal_level: SignalLevel
  signal_reason: string
  entry_zone?: number
  stop_zone?: number
  target_zone?: number
  position_level: PositionLevel
  risk_warning?: string
}

export interface MarketAnalysis {
  update_time: string
  market_state: MarketState
  current_price: number
  price_change: number
  price_change_pct: number
  indicators: TechnicalIndicators
  signal: TradingSignal
  explanation: string
  news_items: NewsItem[]
  // Related assets data
  dxy_price?: number  // 美元指数价格
  dxy_change_pct?: number  // 美元指数变化百分比
  // Real interest rate data
  real_rate?: number  // 实际利率(%)
  nominal_rate?: number  // 名义利率(%)
  inflation_rate?: number  // 通胀率(%)
  // LLM enhanced fields
  llm_explanation?: string  // LLM生成的教学型解释
}

export interface NewsItem {
  news_time: string  // 新闻时间
  title: string  // 新闻标题
  content?: string  // 新闻具体内容
  source?: string  // 来源媒体
  url?: string  // 原文链接
  sentiment?: string  // 情绪倾向(利多/利空/中性)
}

export interface PriceResponse {
  success: boolean
  current_price: number
  price_change: number
  price_change_pct: number
  price_refresh_time: string  // 金价刷新时间(后端时间戳)
}

export interface ChartDataPoint {
  date: string
  price: number
  ma_short?: number
  ma_mid?: number
  support?: number
  resistance?: number
}

export interface ChartData {
  symbol: string
  period: string
  data: ChartDataPoint[]
  key_levels: Record<string, number>
}

export interface OrderLevel {
  price: number
  volume: number
}

export interface MarketDepthResponse {
  bids: OrderLevel[]
  asks: OrderLevel[]
  current_price: number
  best_bid: number
  best_ask: number
  spread: number
  total_bid_volume: number
  total_ask_volume: number
  bid_ask_ratio: number
  data_source: string
  symbol: string
  is_simulated: boolean
}

// API Functions
export const apiAnalysis = {
  // Get market analysis
  getAnalysis: async (period?: string, interval?: string): Promise<MarketAnalysis> => {
    const response = await api.get<MarketAnalysis>('/analysis', {
      params: { period, interval },
    })
    return response.data
  },

  // Refresh data
  refreshData: async (force = false): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/refresh', { force })
    return response.data
  },

  // Get price only (for 10s auto-refresh)
  getPrice: async (): Promise<PriceResponse> => {
    const response = await api.get<PriceResponse>('/price')
    return response.data
  },

  // Get chart data
  getChartData: async (
    symbol = 'GC=F',
    period = '1y',
    interval = '1d'
  ): Promise<ChartData> => {
    const response = await api.get<ChartData>('/chart', {
      params: { symbol, period, interval },
    })
    return response.data
  },

  // Chat query
  sendQuery: async (question: string): Promise<{ answer: string }> => {
    const response = await api.post('/chat', { question })
    return response.data
  },

  // Get market depth (order book) data
  getMarketDepth: async (symbol = 'PAXGUSDT', limit = 10): Promise<MarketDepthResponse> => {
    const response = await api.get<MarketDepthResponse>('/market-depth', {
      params: { symbol, limit },
    })
    return response.data
  },
}

export default api
