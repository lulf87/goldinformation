/**
 * 交易组件类型定义
 */

// 订单类型
export interface Order {
  price: number
  amount: number
  total: number
}

// 市场深度数据
export interface DepthData {
  price: number
  bidVolume: number
  askVolume: number
}

// 价格项
export interface PriceItem {
  symbol: string
  price: number
  change?: number
  changePercent?: number
  time?: string
  currency?: string
}

// 交易表单数据
export interface TradingFormData {
  symbol: string
  orderType: 'market' | 'limit'
  leverage: number
  limitPrice?: number
  amount: number
}

// 新闻项
export interface NewsItem {
  title: string
  summary: string
  sentiment: '利多' | '利空' | '中性'
  time: string
  source?: string
  url?: string
}

// K线数据
export interface KlineData {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

// 市场统计
export interface MarketStats {
  volume24h: number
  openInterest: number
  change24h: number
  longShortRatio: string
}

// 账户信息
export interface AccountInfo {
  balance: number
  position: number
  frozenBalance: number
  frozenPosition: number
}

// 订单结果
export interface OrderResult {
  orderId: string
  symbol: string
  type: 'buy' | 'sell'
  orderType: 'market' | 'limit'
  price: number
  amount: number
  status: 'pending' | 'filled' | 'cancelled'
  createdAt: string
}
