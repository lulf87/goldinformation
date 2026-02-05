/**
 * 交易数据 Store
 * 管理交易相关的状态和数据
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, type OrderLevel } from '@/api'

export const useTradingStore = defineStore('trading', () => {
  // 状态
  const currentPrice = ref(0)
  const priceChange = ref(0)
  const priceChangePercent = ref(0)

  // 订单簿数据
  const orderBookBids = ref<OrderLevel[]>([])
  const orderBookAsks = ref<OrderLevel[]>([])
  const isOrderBookLoading = ref(false)

  // 市场深度数据
  const marketDepthData = ref<{ price: number; bidVolume: number; askVolume: number }[]>([])
  const isMarketDepthLoading = ref(false)

  // 账户信息
  const accountBalance = ref(0)
  const accountPosition = ref(0)

  // 当前订单类型
  const orderType = ref<'buy' | 'sell'>('buy')

  // WebSocket 连接状态
  const wsState = ref<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')

  // 计算属性
  const bestBid = computed(() => {
    if (orderBookBids.value.length === 0) return 0
    return orderBookBids.value[0].price
  })

  const bestAsk = computed(() => {
    if (orderBookAsks.value.length === 0) return 0
    return orderBookAsks.value[0].price
  })

  const spread = computed(() => {
    return bestAsk.value - bestBid.value
  })

  const totalBidVolume = computed(() => {
    return orderBookBids.value.reduce((sum, order) => sum + order.volume, 0)
  })

  const totalAskVolume = computed(() => {
    return orderBookAsks.value.reduce((sum, order) => sum + order.volume, 0)
  })

  // Actions
  const setCurrentPrice = (price: number, change: number, changePercent: number) => {
    currentPrice.value = price
    priceChange.value = change
    priceChangePercent.value = changePercent
  }

  const setOrderBookData = (bids: OrderLevel[], asks: OrderLevel[]) => {
    // 计算累计数量
    let bidTotal = 0
    const bidsWithTotal = bids.map(order => {
      bidTotal += order.volume
      return { ...order, total: bidTotal }
    })

    let askTotal = 0
    const asksWithTotal = asks.map(order => {
      askTotal += order.volume
      return { ...order, total: askTotal }
    })

    orderBookBids.value = bidsWithTotal
    orderBookAsks.value = asksWithTotal
  }

  const setMarketDepthData = (data: { price: number; bidVolume: number; askVolume: number }[]) => {
    marketDepthData.value = data
  }

  const setAccountInfo = (balance: number, position: number) => {
    accountBalance.value = balance
    accountPosition.value = position
  }

  const setOrderType = (type: 'buy' | 'sell') => {
    orderType.value = type
  }

  const setWsState = (state: 'connecting' | 'connected' | 'disconnected' | 'error') => {
    wsState.value = state
  }

  // 获取当前价格
  const fetchCurrentPrice = async () => {
    try {
      const response = await api.apiAnalysis.getPrice()
      setCurrentPrice(
        response.current_price,
        response.price_change,
        response.price_change_pct
      )
    } catch (error) {
      console.error('获取价格失败:', error)
      throw error
    }
  }

  // 获取订单簿数据
  const fetchOrderBook = async () => {
    isOrderBookLoading.value = true
    try {
      const response = await api.apiAnalysis.getMarketDepth()
      setOrderBookData(response.bids, response.asks)
    } catch (error) {
      console.error('获取订单簿失败:', error)
      throw error
    } finally {
      isOrderBookLoading.value = false
    }
  }

  // 获取市场深度
  const fetchMarketDepth = async () => {
    isMarketDepthLoading.value = true
    try {
      const response = await api.apiAnalysis.getMarketDepth()

      // 转换数据格式
      const depthData = response.bids.map((bid, index) => ({
        price: bid.price,
        bidVolume: bid.volume,
        askVolume: response.asks[index]?.volume || 0,
      }))

      setMarketDepthData(depthData)
    } catch (error) {
      console.error('获取市场深度失败:', error)
      throw error
    } finally {
      isMarketDepthLoading.value = false
    }
  }

  // 刷新所有数据
  const refreshAllData = async () => {
    try {
      await Promise.all([
        fetchCurrentPrice(),
        fetchOrderBook(),
        fetchMarketDepth(),
      ])
    } catch (error) {
      console.error('刷新数据失败:', error)
    }
  }

  return {
    // State
    currentPrice,
    priceChange,
    priceChangePercent,
    orderBookBids,
    orderBookAsks,
    isOrderBookLoading,
    marketDepthData,
    isMarketDepthLoading,
    accountBalance,
    accountPosition,
    orderType,
    wsState,

    // Computed
    bestBid,
    bestAsk,
    spread,
    totalBidVolume,
    totalAskVolume,

    // Actions
    setCurrentPrice,
    setOrderBookData,
    setMarketDepthData,
    setAccountInfo,
    setOrderType,
    setWsState,

    // Methods
    fetchCurrentPrice,
    fetchOrderBook,
    fetchMarketDepth,
    refreshAllData,
  }
})
