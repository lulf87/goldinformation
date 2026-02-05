/**
 * 交易组件库统一导出
 *
 * 使用方式:
 * import { OrderBook, MarketDepth, TradingForm, RealtimePriceTicker } from '@/components/trading'
 */

// 交易组件
export { default as OrderBook } from './OrderBook.vue'
export { default as MarketDepth } from './MarketDepth.vue'
export { default as TradingForm } from './TradingForm.vue'
export { default as RealtimePriceTicker } from './RealtimePriceTicker.vue'

// 类型定义
export type { Order, DepthData, PriceItem, TradingFormData } from './types.ts'
