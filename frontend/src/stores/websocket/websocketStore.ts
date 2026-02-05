/**
 * WebSocket Store
 * 管理 WebSocket 连接和实时数据
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  createWebSocketService,
  getWebSocketService,
  destroyWebSocketService,
  destroyWebSocketService as destroyWsService,
  type WebSocketService,
  type ConnectionState,
  type WSPriceData,
  type WSOrderBookData,
  type WSMarketDepthData,
} from '@/services/websocket'

export const useWebSocketStore = defineStore('websocket', () => {
  // WebSocket 服务实例
  let wsService: WebSocketService | null = null

  // 连接状态
  const connectionState = ref<ConnectionState>('disconnected')
  const lastMessageTime = ref(0)
  const messageCount = ref(0)

  // 实时价格数据
  const realtimePrices = ref<Map<string, WSPriceData>>(new Map())

  // 是否自动重连
  const autoReconnect = ref(true)

  // WebSocket URL
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

  // 连接 WebSocket
  const connect = () => {
    if (wsService) {
      console.log('[WebSocket] 已存在连接，先断开')
      disconnect()
    }

    wsService = createWebSocketService(wsUrl)

    // 设置回调
    wsService.onPrice((data: WSPriceData) => {
      handlePriceData(data)
    })

    wsService.onOrderBook((data: WSOrderBookData) => {
      handleOrderBookData(data)
    })

    wsService.onMarketDepth((data: WSMarketDepthData) => {
      handleMarketDepthData(data)
    })

    wsService.onStateChange((state: ConnectionState) => {
      connectionState.value = state
    })

    // 连接
    wsService.connect()
  }

  // 断开连接
  const disconnect = () => {
    if (wsService) {
      wsService.disconnect()
      wsService = null
    }
    connectionState.value = 'disconnected'
  }

  // 处理价格数据
  const handlePriceData = (data: WSPriceData) => {
    realtimePrices.value.set(data.symbol, data)
    lastMessageTime.value = Date.now()
    messageCount.value++
  }

  // 处理订单簿数据
  const handleOrderBookData = (data: WSOrderBookData) => {
    lastMessageTime.value = Date.now()
    messageCount.value++
    // 这里可以触发 store 的 action 来更新订单簿数据
  }

  // 处理市场深度数据
  const handleMarketDepthData = (data: WSMarketDepthData) => {
    lastMessageTime.value = Date.now()
    messageCount.value++
    // 这里可以触发 store 的 action 来更新市场深度数据
  }

  // 获取实时价格
  const getRealtimePrice = (symbol: string) => {
    return realtimePrices.value.get(symbol)
  }

  // 发送消息
  const send = (type: string, data: any) => {
    wsService?.send(type, data)
  }

  // 订阅数据
  const subscribe = (symbols: string[]) => {
    wsService?.subscribe(symbols)
  }

  // 取消订阅
  const unsubscribe = (symbols: string[]) => {
    wsService?.unsubscribe(symbols)
  }

  // 获取连接统计
  const getConnectionStats = computed(() => {
    return wsService ? wsService.getStats() : null
  })

  // 初始化时自动连接
  const initialize = () => {
    if (autoReconnect.value) {
      connect()
    }
  }

  // 清理
  const cleanup = () => {
    disconnect()
    destroyWebSocketService()
  }

  return {
    // State
    connectionState,
    lastMessageTime,
    messageCount,
    realtimePrices,
    autoReconnect,

    // Actions
    connect,
    disconnect,
    initialize,
    cleanup,

    // Methods
    getRealtimePrice,
    send,
    subscribe,
    unsubscribe,

    // Computed
    getConnectionStats,
  }
})
