<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-[#F8FAFC] flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        市场深度
      </h2>
      <div class="flex items-center gap-2">
        <span v-if="loading" class="text-xs text-slate-400">加载中...</span>
        <span v-else-if="isSimulated" class="text-xs text-amber-400">模拟数据</span>
        <span v-else class="text-xs text-emerald-400 flex items-center gap-1">
          <span class="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
          {{ dataSource }}
        </span>
      </div>
    </div>

    <!-- Order Book -->
    <div class="space-y-2">
      <!-- Sell Orders (Asks) -->
      <div class="space-y-1">
        <div class="flex items-center justify-between text-xs text-slate-500 px-2">
          <span>卖单</span>
          <span>数量</span>
          <span>价格</span>
        </div>
        <div
          v-for="(ask, index) in reversedAsks"
          :key="'ask-' + index"
          class="relative flex items-center justify-between px-3 py-2 rounded bg-slate-700/20 hover:bg-slate-700/40 transition-colors"
        >
          <!-- Background bar based on volume -->
          <div
            class="absolute inset-y-0 right-0 bg-red-500/10 rounded"
            :style="{ width: (ask.volume / maxVolume * 100) + '%' }"
          ></div>

          <span class="relative z-10 text-sm text-red-300 w-20">{{ formatPrice(ask.price) }}</span>
          <span class="relative z-10 text-sm text-slate-300 font-mono">{{ formatVolume(ask.volume) }}</span>
          <span class="relative z-10 text-xs text-slate-500 w-16 text-right">{{ ((ask.volume / totalVolume) * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <!-- Current Price Spread -->
      <div class="flex items-center justify-between py-3 px-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
        <div class="text-center flex-1">
          <p class="text-xs text-slate-500 mb-1">买一</p>
          <p class="text-lg font-semibold text-emerald-400 mono-number">{{ formatPrice(bestBid) }}</p>
        </div>
        <div class="flex flex-col items-center px-4">
          <p class="text-2xl font-bold text-[#F59E0B] mono-number">{{ formatPrice(currentPrice) }}</p>
          <p class="text-xs text-slate-500 mt-1">当前价</p>
        </div>
        <div class="text-center flex-1">
          <p class="text-xs text-slate-500 mb-1">卖一</p>
          <p class="text-lg font-semibold text-red-400 mono-number">{{ formatPrice(bestAsk) }}</p>
        </div>
      </div>

      <!-- Buy Orders (Bids) -->
      <div class="space-y-1">
        <div class="flex items-center justify-between text-xs text-slate-500 px-2">
          <span>买单</span>
          <span>数量</span>
          <span>价格</span>
        </div>
        <div
          v-for="(bid, index) in bids"
          :key="'bid-' + index"
          class="relative flex items-center justify-between px-3 py-2 rounded bg-slate-700/20 hover:bg-slate-700/40 transition-colors"
        >
          <!-- Background bar based on volume -->
          <div
            class="absolute inset-y-0 right-0 bg-emerald-500/10 rounded"
            :style="{ width: (bid.volume / maxVolume * 100) + '%' }"
          ></div>

          <span class="relative z-10 text-sm text-emerald-300 w-20">{{ formatPrice(bid.price) }}</span>
          <span class="relative z-10 text-sm text-slate-300 font-mono">{{ formatVolume(bid.volume) }}</span>
          <span class="relative z-10 text-xs text-slate-500 w-16 text-right">{{ ((bid.volume / totalVolume) * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <!-- Depth Summary -->
    <div class="mt-4 pt-4 border-t border-slate-700/50">
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <p class="text-xs text-slate-500">买量</p>
          <p class="text-sm font-semibold text-emerald-400 mono-number mt-1">{{ formatVolume(totalBidVolume) }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-500">买卖比</p>
          <p class="text-sm font-semibold text-[#F59E0B] mono-number mt-1">{{ bidAskRatio.toFixed(2) }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-500">卖量</p>
          <p class="text-sm font-semibold text-red-400 mono-number mt-1">{{ formatVolume(totalAskVolume) }}</p>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
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
    error.value = '获取市场深度数据失败，使用模拟数据'
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
/* Ensure smooth transitions for order book updates */
.transition-colors {
  transition: background-color var(--duration-normal) ease-out;
}
</style>
