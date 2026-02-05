<template>
  <div class="market-depth-card">
    <div class="card-header">
      <h2 class="card-title">
        <svg class="title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        市场深度
      </h2>
      <div class="card-status">
        <span v-if="loading" class="status-badge status-loading">加载中...</span>
        <span v-else-if="isSimulated" class="status-badge status-simulated">模拟数据</span>
        <span v-else class="status-badge status-live">
          <span class="live-indicator"></span>
          {{ dataSource }}
        </span>
      </div>
    </div>

    <!-- Order Book -->
    <div class="order-book">
      <!-- Sell Orders (Asks) -->
      <div class="order-section">
        <div class="order-header">
          <span>卖单</span>
          <span>数量</span>
          <span>价格</span>
        </div>
        <div
          v-for="(ask, index) in reversedAsks"
          :key="'ask-' + index"
          class="order-row order-row-ask"
        >
          <!-- Background bar based on volume -->
          <div
            class="order-bar order-bar-ask"
            :style="{ width: (ask.volume / maxVolume * 100) + '%' }"
          ></div>

          <span class="order-price order-price-ask">{{ formatPrice(ask.price) }}</span>
          <span class="order-volume">{{ formatVolume(ask.volume) }}</span>
          <span class="order-percent">{{ ((ask.volume / totalVolume) * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <!-- Current Price Spread -->
      <div class="price-spread">
        <div class="price-info price-info-bid">
          <p class="price-label">买一</p>
          <p class="price-value price-value-bid mono-number">{{ formatPrice(bestBid) }}</p>
        </div>
        <div class="price-info price-info-current">
          <p class="price-value price-value-main mono-number">{{ formatPrice(currentPrice) }}</p>
          <p class="price-label">当前价</p>
        </div>
        <div class="price-info price-info-ask">
          <p class="price-label">卖一</p>
          <p class="price-value price-value-ask mono-number">{{ formatPrice(bestAsk) }}</p>
        </div>
      </div>

      <!-- Buy Orders (Bids) -->
      <div class="order-section">
        <div class="order-header">
          <span>买单</span>
          <span>数量</span>
          <span>价格</span>
        </div>
        <div
          v-for="(bid, index) in bids"
          :key="'bid-' + index"
          class="order-row order-row-bid"
        >
          <!-- Background bar based on volume -->
          <div
            class="order-bar order-bar-bid"
            :style="{ width: (bid.volume / maxVolume * 100) + '%' }"
          ></div>

          <span class="order-price order-price-bid">{{ formatPrice(bid.price) }}</span>
          <span class="order-volume">{{ formatVolume(bid.volume) }}</span>
          <span class="order-percent">{{ ((bid.volume / totalVolume) * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <!-- Depth Summary -->
    <div class="depth-summary">
      <div class="summary-item">
        <p class="summary-label">买量</p>
        <p class="summary-value summary-value-bid mono-number">{{ formatVolume(totalBidVolume) }}</p>
      </div>
      <div class="summary-item">
        <p class="summary-label">买卖比</p>
        <p class="summary-value summary-value-ratio mono-number">{{ bidAskRatio.toFixed(2) }}</p>
      </div>
      <div class="summary-item">
        <p class="summary-label">卖量</p>
        <p class="summary-value summary-value-ask mono-number">{{ formatVolume(totalAskVolume) }}</p>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { apiAnalysis, type OrderLevel, type MarketDepthResponse } from '@/api'

// State
const asks = ref<OrderLevel[]>([])
const bids = ref<OrderLevel[]>([])
const currentPrice = ref(0)
const bestBid = ref(0)
const bestAsk = ref(0)
const totalBidVolume = ref(0)
const totalAskVolume = ref(0)
const bidAskRatio = ref(0)
const dataSource = ref('Binance (PAXG)')
const isSimulated = ref(true)
const loading = ref(true)
const error = ref<string | null>(null)

// Fetch market depth data from API
async function fetchMarketDepth() {
  try {
    error.value = null
    const data: MarketDepthResponse = await apiAnalysis.getMarketDepth('PAXGUSDT', 5)

    asks.value = data.asks
    bids.value = data.bids
    currentPrice.value = data.current_price
    bestBid.value = data.best_bid
    bestAsk.value = data.best_ask
    totalBidVolume.value = data.total_bid_volume
    totalAskVolume.value = data.total_ask_volume
    bidAskRatio.value = data.bid_ask_ratio
    dataSource.value = data.data_source
    isSimulated.value = data.is_simulated

    loading.value = false
  } catch (e) {
    console.error('Failed to fetch market depth:', e)
    error.value = '获取市场深度数据失败,使用模拟数据'
    // Fallback to simulated data
    generateMockOrderBook()
    isSimulated.value = true
    loading.value = false
  }
}

// Generate mock order book data (fallback)
function generateMockOrderBook() {
  const basePrice = 2745.30
  const askData: OrderLevel[] = []
  const bidData: OrderLevel[] = []

  // Generate asks (sells) - prices above current
  for (let i = 0; i < 5; i++) {
    askData.push({
      price: basePrice + (i + 1) * 0.5 + Math.random() * 0.3,
      volume: Math.floor(Math.random() * 5) + 1,
    })
  }

  // Generate bids (buys) - prices below current
  for (let i = 0; i < 5; i++) {
    bidData.push({
      price: basePrice - (i + 1) * 0.5 - Math.random() * 0.3,
      volume: Math.floor(Math.random() * 5) + 1,
    })
  }

  asks.value = askData
  bids.value = bidData
  currentPrice.value = basePrice
  bestBid.value = bidData[0]?.price || basePrice
  bestAsk.value = askData[0]?.price || basePrice
  totalBidVolume.value = bidData.reduce((sum, b) => sum + b.volume, 0)
  totalAskVolume.value = askData.reduce((sum, a) => sum + a.volume, 0)
  bidAskRatio.value = totalBidVolume.value / (totalAskVolume.value || 1)
  dataSource.value = '模拟'
}

// Computed properties
const reversedAsks = computed(() => {
  return [...asks.value].reverse()
})

const maxVolume = computed(() => {
  const allVolumes = [...asks.value, ...bids.value].map((o) => o.volume)
  return Math.max(...allVolumes, 0.001)
})

const totalVolume = computed(() => {
  return [...asks.value, ...bids.value].reduce((sum, o) => sum + o.volume, 0) || 1
})

// Format helpers
function formatPrice(price: number): string {
  return price.toFixed(2)
}

function formatVolume(volume: number): string {
  if (volume >= 1000) {
    return (volume / 1000).toFixed(1) + 'K'
  }
  return volume.toFixed(4)
}

// Update order book periodically
let orderBookTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // Initial fetch
  fetchMarketDepth()

  // Update every 3 seconds
  orderBookTimer = setInterval(() => {
    fetchMarketDepth()
  }, 3000)
})

onUnmounted(() => {
  if (orderBookTimer) {
    clearInterval(orderBookTimer)
  }
})
</script>

<style scoped>
/* Card */
.market-depth-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

/* Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.title-icon {
  width: var(--icon-md);
  height: var(--icon-md);
}

.card-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.status-badge {
  font-size: var(--text-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.status-loading {
  color: var(--color-text-muted);
  background: var(--color-bg-elevated);
}

.status-simulated {
  color: var(--color-warning);
  background: rgba(245, 158, 11, 0.1);
}

.status-live {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.1);
}

.live-indicator {
  width: 6px;
  height: 6px;
  background: var(--color-success);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Order Book */
.order-book {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.order-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  padding: 0 var(--spacing-sm);
}

.order-row {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-base) var(--ease-default);
}

.order-row-ask {
  background: rgba(239, 68, 68, 0.05);
}

.order-row-ask:hover {
  background: rgba(239, 68, 68, 0.1);
}

.order-row-bid {
  background: rgba(16, 185, 129, 0.05);
}

.order-row-bid:hover {
  background: rgba(16, 185, 129, 0.1);
}

.order-bar {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  pointer-events: none;
}

.order-bar-ask {
  background: rgba(239, 68, 68, 0.1);
  right: 0;
}

.order-bar-bid {
  background: rgba(16, 185, 129, 0.1);
  right: 0;
}

.order-price {
  position: relative;
  z-index: 1;
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  font-weight: 500;
  width: 5rem;
}

.order-price-ask {
  color: var(--color-error);
}

.order-price-bid {
  color: var(--color-success);
}

.order-volume {
  position: relative;
  z-index: 1;
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
}

.order-percent {
  position: relative;
  z-index: 1;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  width: 4rem;
  text-align: right;
}

/* Price Spread */
.price-spread {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--glass-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.price-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.price-info-bid,
.price-info-ask {
  flex: 1;
}

.price-info-current {
  padding: 0 var(--spacing-md);
}

.price-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.price-value {
  font-size: var(--text-lg);
  font-weight: 600;
  margin: 0;
}

.price-value-bid {
  color: var(--color-success);
}

.price-value-ask {
  color: var(--color-error);
}

.price-value-main {
  font-size: var(--text-2xl);
  color: var(--color-warning);
}

/* Depth Summary */
.depth-summary {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  text-align: center;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.summary-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.summary-value {
  font-size: var(--text-sm);
  font-weight: 600;
  margin: 0;
}

.summary-value-bid {
  color: var(--color-success);
}

.summary-value-ratio {
  color: var(--color-warning);
}

.summary-value-ask {
  color: var(--color-error);
}

/* Error Message */
.error-message {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  color: var(--color-error);
}

/* Mono Number Font */
.mono-number {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

/* Responsive */
@media (max-width: 768px) {
  .market-depth-card {
    padding: var(--spacing-md);
  }

  .price-spread {
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .price-value-main {
    font-size: var(--text-xl);
  }
}
</style>
