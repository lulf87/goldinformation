/**
 * WebSocket 服务
 * 用于实时接收价格推送和市场数据更新
 */

import { ref, computed } from 'vue'

// WebSocket 连接状态
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error'

// WebSocket 消息类型
export interface WSMessage {
  type: 'price' | 'orderbook' | 'market_depth' | 'trade' | 'news' | 'heartbeat'
  data: any
  timestamp: number
}

// 价格推送数据
export interface WSPriceData {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume?: number
}

// 订单簿推送数据
export interface WSOrderBookData {
  symbol: string
  bids: { price: number; amount: number; total: number }[]
  asks: { price: number; amount: number; total: number }[]
}

// 市场深度推送数据
export interface WSMarketDepthData {
  symbol: string
  data: { price: number; bidVolume: number; askVolume: number }[]
}

// 成交推送数据
export interface WSTradeData {
  symbol: string
  price: number
  amount: number
  type: 'buy' | 'sell'
  timestamp: string
}

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private heartbeatInterval: NodeJS.Timeout | null = null

  // 状态
  private connectionState = ref<ConnectionState>('disconnected')
  private lastMessageTime = ref(0)
  private messageCount = ref(0)

  // 回调函数
  private onPriceCallback: ((data: WSPriceData) => void) | null = null
  private onOrderBookCallback: ((data: WSOrderBookData) => void) | null = null
  private onMarketDepthCallback: ((data: WSMarketDepthData) => void) | null = null
  private onTradeCallback: ((data: WSTradeData) => void) | null = null
  private onNewsCallback: ((data: any) => void) | null = null
  private onStateChangeCallback: ((state: ConnectionState) => void) | null = null

  constructor(url: string) {
    this.url = url
  }

  // 连接 WebSocket
  connect(): void {
    if (this.connectionState.value === 'connected' || this.connectionState.value === 'connecting') {
      return
    }

    this.connectionState.value = 'connecting'
    this.notifyStateChange()

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onerror = this.handleError.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
    } catch (error) {
      console.error('[WebSocket] 连接失败:', error)
      this.connectionState.value = 'error'
      this.notifyStateChange()
    }
  }

  // 断开连接
  disconnect(): void {
    this.stopHeartbeat()

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.connectionState.value = 'disconnected'
    this.reconnectAttempts = 0
    this.notifyStateChange()
  }

  // 设置回调函数
  onPrice(callback: (data: WSPriceData) => void): void {
    this.onPriceCallback = callback
  }

  onOrderBook(callback: (data: WSOrderBookData) => void): void {
    this.onOrderBookCallback = callback
  }

  onMarketDepth(callback: (data: WSMarketDepthData) => void): void {
    this.onMarketDepthCallback = callback
  }

  onTrade(callback: (data: WSTradeData) => void): void {
    this.onTradeCallback = callback
  }

  onNews(callback: (data: any) => void): void {
    this.onNewsCallback = callback
  }

  onStateChange(callback: (state: ConnectionState) => void): void {
    this.onStateChangeCallback = callback
  }

  // 发送消息
  send(type: string, data: any): void {
    if (this.connectionState.value !== 'connected') {
      console.warn('[WebSocket] 未连接，无法发送消息')
      return
    }

    const message: WSMessage = {
      type,
      data,
      timestamp: Date.now(),
    }

    try {
      this.ws?.send(JSON.stringify(message))
    } catch (error) {
      console.error('[WebSocket] 发送消息失败:', error)
    }
  }

  // 订阅数据
  subscribe(symbols: string[]): void {
    this.send('subscribe', { symbols })
  }

  // 取消订阅
  unsubscribe(symbols: string[]): void {
    this.send('unsubscribe', { symbols })
  }

  // 处理连接打开
  private handleOpen(): void {
    console.log('[WebSocket] 连接成功')
    this.connectionState.value = 'connected'
    this.reconnectAttempts = 0
    this.notifyStateChange()

    // 启动心跳
    this.startHeartbeat()

    // 订阅初始数据
    this.send('subscribe', { symbols: ['AU9999', 'XAU/USD'] })
  }

  // 处理接收消息
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WSMessage = JSON.parse(event.data)
      this.lastMessageTime.value = Date.now()
      this.messageCount.value++

      // 根据消息类型分发
      switch (message.type) {
        case 'price':
          this.onPriceCallback?.(message.data as WSPriceData)
          break
        case 'orderbook':
          this.onOrderBookCallback?.(message.data as WSOrderBookData)
          break
        case 'market_depth':
          this.onMarketDepthCallback?.(message.data as WSMarketDepthData)
          break
        case 'trade':
          this.onTradeCallback?.(message.data as WSTradeData)
          break
        case 'news':
          this.onNewsCallback?.(message.data)
          break
        case 'heartbeat':
          // 心跳响应，无需处理
          break
        default:
          console.warn('[WebSocket] 未知消息类型:', message.type)
      }
    } catch (error) {
      console.error('[WebSocket] 解析消息失败:', error)
    }
  }

  // 处理错误
  private handleError(error: Event): void {
    console.error('[WebSocket] 错误:', error)
    this.connectionState.value = 'error'
    this.notifyStateChange()
  }

  // 处理连接关闭
  private handleClose(): void {
    console.log('[WebSocket] 连接关闭')
    this.stopHeartbeat()
    this.connectionState.value = 'disconnected'
    this.notifyStateChange()

    // 尝试重连
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`[WebSocket] 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

      setTimeout(() => {
        this.connect()
      }, this.reconnectDelay)
    } else {
      console.error('[WebSocket] 达到最大重连次数，放弃重连')
    }
  }

  // 启动心跳
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.connectionState.value === 'connected') {
        this.send('ping', {})
      }
    }, 30000) // 每30秒发送一次心跳
  }

  // 停止心跳
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  // 通知状态变化
  private notifyStateChange(): void {
    this.onStateChangeCallback?.(this.connectionState.value)
  }

  // 获取连接状态
  getState(): ConnectionState {
    return this.connectionState.value
  }

  // 获取统计信息
  getStats() {
    return {
      state: this.connectionState.value,
      lastMessageTime: this.lastMessageTime.value,
      messageCount: this.messageCount.value,
    }
  }
}

// 导出单例
let wsService: WebSocketService | null = null

export function createWebSocketService(url: string): WebSocketService {
  if (!wsService) {
    wsService = new WebSocketService(url)
  }
  return wsService
}

export function getWebSocketService(): WebSocketService | null {
  return wsService
}

export function destroyWebSocketService(): void {
  if (wsService) {
    wsService.disconnect()
    wsService = null
  }
}
