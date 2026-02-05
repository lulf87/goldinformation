import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types - 增强版
export type MarketState = 
  | 'strong_bull'      // 强势上涨
  | 'bull_trend'       // 上涨趋势
  | 'range'            // 区间震荡
  | 'bear_trend'       // 下跌趋势
  | 'strong_bear'      // 强势下跌
  | 'high_volatility'  // 高波动
  | 'unclear'          // 不清晰
  | 'trend'            // 兼容旧代码

export type SignalLevel = 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
export type PositionLevel = 'low' | 'medium' | 'high'

export interface TechnicalIndicators {
  // 移动平均线
  ma_short?: number      // 短期均线 (20)
  ma_mid?: number        // 中期均线 (60)
  ema_short?: number     // 短期EMA (12)
  ema_long?: number      // 长期EMA (26)
  
  // 趋势指标
  trend_dir?: string     // 趋势方向 (up/down/neutral)
  trend_strength?: string  // 趋势强度 (weak/medium/strong)
  adx?: number           // ADX 趋势强度指标 (0-100)
  plus_di?: number       // +DI 方向指标
  minus_di?: number      // -DI 方向指标
  
  // 动量指标
  rsi?: number           // RSI 相对强弱指数 (0-100)
  rsi_state?: string     // RSI 状态 (oversold/neutral/overbought)
  macd?: number          // MACD 线
  macd_signal?: number   // MACD 信号线
  macd_hist?: number     // MACD 柱状图
  macd_cross?: string    // MACD 交叉 (golden/dead/none)
  
  // 波动指标
  atr?: number           // ATR 波动度
  vol_state?: string     // 波动状态 (low/medium/high)
  bb_upper?: number      // 布林带上轨
  bb_middle?: number     // 布林带中轨
  bb_lower?: number      // 布林带下轨
  bb_width?: number      // 布林带宽度 (%)
  bb_position?: string   // 价格在布林带位置 (above/upper/middle/lower/below)
  
  // 支撑阻力
  support_level?: number
  resistance_level?: number
  range_high?: number
  range_low?: number
  range_mid?: number
}

// 因子详情
export interface FactorDetail {
  score: number
  weight: number
}

export interface TradingSignal {
  signal_level: SignalLevel
  signal_reason: string
  entry_zone?: number
  stop_zone?: number
  target_zone?: number
  position_level: PositionLevel
  risk_warning?: string
  
  // 新增：置信度和评分
  confidence?: number           // 信号置信度 (0-100%)
  technical_score?: number      // 技术面评分 (-100 到 +100)
  sentiment_score?: number      // 情感面评分 (-100 到 +100)
  composite_score?: number      // 综合评分 (-100 到 +100)
  
  // 新增：因子详情
  factor_details?: Record<string, FactorDetail>
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
  reason?: string  // 影响分析
  relevance?: string  // 相关性(高/中/低)
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

export interface GoldPriceItem {
  price: number
  change?: number
  change_pct?: number
  update_time: string
  data_source: string
  is_available: boolean
  unit: string
  error?: string
}

export interface GoldPricesResponse {
  london_gold: GoldPriceItem
  au9999: GoldPriceItem
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

  // Get gold prices from multiple markets
  getGoldPrices: async (): Promise<GoldPricesResponse> => {
    const response = await api.get<GoldPricesResponse>('/gold-prices')
    return response.data
  },
}

export default api
