<template>
  <div class="min-h-screen bg-slate-900">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-slate-800/90 backdrop-blur border-b border-slate-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-slate-100">黄金交易 Agent</h1>
            <p class="text-sm text-slate-400 mt-1">
              金价刷新时间: {{ priceRefreshTime }}
            </p>
          </div>
          <button
            @click="handleRefresh"
            :disabled="store.loading"
            class="btn btn-primary flex items-center gap-2"
            :class="{ 'opacity-50 cursor-wait': store.loading }"
          >
            <svg v-if="!store.loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ store.loading ? '刷新中...' : '刷新数据' }}
          </button>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="store.loading && !store.analysis" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-slate-400">正在加载市场数据...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="card bg-red-900/20 border-red-800">
        <p class="text-red-400">{{ store.error }}</p>
        <button @click="store.fetchAnalysis()" class="btn btn-primary mt-4">重试</button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="store.analysis" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <!-- Signal Card -->
      <section class="card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-slate-200">交易信号</h2>
          <span :class="['signal-badge', store.signalLevelClass]">
            {{ signalLabel }}
          </span>
        </div>
        <p class="text-slate-300">{{ store.analysis.signal.signal_reason }}</p>
      </section>

      <!-- Price Overview -->
      <section class="card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-slate-200">行情概览</h2>
          <button
            @click="handlePriceRefresh"
            :disabled="priceRefreshing"
            class="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-100 transition-colors"
            :class="{ 'opacity-50 cursor-wait': priceRefreshing }"
            title="刷新金价"
          >
            <svg
              class="w-4 h-4"
              :class="{ 'animate-spin': priceRefreshing }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p class="text-sm text-slate-400">当前价格</p>
            <p class="text-2xl font-mono font-bold mt-1">
              ${{ store.analysis.current_price.toFixed(2) }}
            </p>
          </div>
          <div>
            <p class="text-sm text-slate-400">价格变化</p>
            <p class="text-2xl font-mono mt-1" :class="store.priceChangeClass">
              {{ store.priceChangeSign }}${{ Math.abs(store.analysis.price_change).toFixed(2) }}
            </p>
          </div>
          <div>
            <p class="text-sm text-slate-400">涨跌幅</p>
            <p class="text-2xl font-mono mt-1" :class="store.priceChangeClass">
              {{ store.priceChangeSign }}{{ Math.abs(store.analysis.price_change_pct).toFixed(2) }}%
            </p>
          </div>
        </div>
      </section>

      <!-- Market State -->
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-200 mb-4">市场状态</h2>
        <div class="flex items-center gap-4">
          <div class="flex-1">
            <p class="text-sm text-slate-400">当前模式</p>
            <p class="text-lg font-semibold mt-1">{{ marketStateLabel }}</p>
          </div>
          <div v-if="store.analysis.indicators.trend_dir" class="flex-1">
            <p class="text-sm text-slate-400">趋势方向</p>
            <p class="text-lg font-semibold mt-1">{{ trendDirectionLabel }}</p>
          </div>
        </div>
      </section>

      <!-- Price Chart -->
      <PriceChart
        :period="store.analysisPeriod"
        @update:period="handlePeriodChange"
      />

      <!-- Key Levels -->
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-200 mb-4">关键价位</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-if="store.analysis.indicators.support_level">
            <p class="text-sm text-slate-400">支撑位</p>
            <p class="text-lg font-mono font-semibold text-emerald-400 mt-1">
              {{ store.analysis.indicators.support_level.toFixed(2) }}
            </p>
          </div>
          <div v-if="store.analysis.indicators.resistance_level">
            <p class="text-sm text-slate-400">阻力位</p>
            <p class="text-lg font-mono font-semibold text-red-400 mt-1">
              {{ store.analysis.indicators.resistance_level.toFixed(2) }}
            </p>
          </div>
          <div v-if="store.analysis.indicators.range_low">
            <p class="text-sm text-slate-400">区间下沿</p>
            <p class="text-lg font-mono font-semibold text-slate-300 mt-1">
              {{ store.analysis.indicators.range_low.toFixed(2) }}
            </p>
          </div>
          <div v-if="store.analysis.indicators.range_high">
            <p class="text-sm text-slate-400">区间上沿</p>
            <p class="text-lg font-mono font-semibold text-slate-300 mt-1">
              {{ store.analysis.indicators.range_high.toFixed(2) }}
            </p>
          </div>
        </div>
      </section>

      <!-- Trading Suggestions -->
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-200 mb-4">操作建议</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p class="text-sm text-slate-400">建议入场区</p>
            <p class="text-lg font-mono font-semibold text-primary mt-1">
              {{ store.analysis.signal.entry_zone !== undefined && store.analysis.signal.entry_zone !== null
                ? store.analysis.signal.entry_zone.toFixed(2)
                : '暂无' }}
            </p>
          </div>
          <div>
            <p class="text-sm text-slate-400">建议止损区</p>
            <p class="text-lg font-mono font-semibold text-red-400 mt-1">
              {{ store.analysis.signal.stop_zone !== undefined && store.analysis.signal.stop_zone !== null
                ? store.analysis.signal.stop_zone.toFixed(2)
                : '暂无' }}
            </p>
          </div>
          <div>
            <p class="text-sm text-slate-400">建议目标区</p>
            <p class="text-lg font-mono font-semibold text-emerald-400 mt-1">
              {{ store.analysis.signal.target_zone !== undefined && store.analysis.signal.target_zone !== null
                ? store.analysis.signal.target_zone.toFixed(2)
                : '暂无' }}
            </p>
          </div>
        </div>
      </section>

      <!-- Position & Risk -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Position Suggestion -->
        <div class="card">
          <h2 class="text-lg font-semibold text-slate-200 mb-4">仓位建议</h2>
          <p class="text-2xl font-bold mt-2" :class="positionLevelClass">
            {{ positionLevelLabel }}
          </p>
        </div>

        <!-- Risk Warning -->
        <div v-if="store.analysis.signal.risk_warning" class="card bg-orange-900/20 border-orange-800">
          <h2 class="text-lg font-semibold text-orange-400 mb-2">⚠️ 风险提示</h2>
          <p class="text-slate-300">{{ store.analysis.signal.risk_warning }}</p>
        </div>
      </section>

      <!-- News Events -->
      <section class="grid grid-cols-1 gap-6">
        <div v-if="store.analysis.news_items && store.analysis.news_items.length > 0" class="card">
          <h2 class="text-lg font-semibold text-slate-200 mb-4">
            📰 新闻事件
          </h2>

          <div class="space-y-3">
            <div
              v-for="(news, index) in store.analysis.news_items.slice(0, 5)"
              :key="index"
              class="p-3 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 transition-colors cursor-pointer border border-slate-700/50"
              @click="toggleNewsExpansion(index)"
            >
              <div class="flex items-start gap-3">
                <!-- Sentiment Badge -->
                <span
                  class="shrink-0 text-xs px-2 py-1 rounded-md font-medium"
                  :class="getSentimentBadgeClass(news.sentiment)"
                >
                  {{ news.sentiment || '中性' }}
                </span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-slate-200 font-medium">{{ news.title }}</p>
                  <p class="text-xs text-slate-400 mt-1">{{ news.news_time }}</p>
                  <!-- Impact Reason (影响解读) -->
                  <p v-if="news.reason" class="text-xs text-slate-400 mt-2 italic">
                    💡 {{ news.reason }}
                  </p>
                </div>
                <span class="text-xs text-slate-500 transition-transform duration-200 shrink-0" :class="{ 'rotate-90': expandedNews.has(index) }">
                  ▶
                </span>
              </div>

              <!-- Expanded content -->
              <div v-if="expandedNews.has(index)" class="mt-3 p-3 bg-slate-900/50 rounded border border-slate-700/50" @click.stop>
                <p v-if="news.content" class="text-sm text-slate-300 leading-relaxed">{{ news.content }}</p>
                <div class="flex items-center gap-4 mt-3">
                  <p v-if="news.source" class="text-xs text-slate-400">来源: {{ news.source }}</p>
                  <a
                    v-if="news.url"
                    :href="news.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-xs text-blue-400 hover:text-blue-300 hover:underline inline-flex items-center gap-1"
                  >
                    阅读全文 →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Related Assets (DXY & Real Rate) -->
      <section v-if="store.analysis.dxy_price || store.analysis.real_rate !== null" class="card">
        <h2 class="text-lg font-semibold text-slate-200 mb-4">💱 关联市场指标</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- DXY Card -->
          <div v-if="store.analysis.dxy_price" class="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-slate-300">美元指数 (DXY)</h3>
              <span
                class="text-xs px-2 py-1 rounded"
                :class="store.analysis.dxy_change_pct! > 0 ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'"
              >
                {{ store.analysis.dxy_change_pct! > 0 ? '↑' : '↓' }}
                {{ Math.abs(store.analysis.dxy_change_pct!).toFixed(2) }}%
              </span>
            </div>
            <p class="text-2xl font-bold text-slate-100">{{ store.analysis.dxy_price.toFixed(2) }}</p>
            <p class="text-xs text-slate-400 mt-1">
              <span v-if="store.analysis.dxy_change_pct! > 0.5">
                📉 美元走强可能对黄金形成压力
              </span>
              <span v-else-if="store.analysis.dxy_change_pct! < -0.5">
                📈 美元走弱可能对黄金形成支撑
              </span>
              <span v-else>
                ➡️ 美元指数相对稳定
              </span>
            </p>
          </div>

          <!-- Real Interest Rate Card -->
          <div v-if="store.analysis.real_rate !== null" class="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-slate-300">实际利率</h3>
              <span
                class="text-xs px-2 py-1 rounded"
                :class="store.analysis.real_rate! > 2 ? 'bg-red-500/20 text-red-300' : store.analysis.real_rate! < 0 ? 'bg-green-500/20 text-green-300' : 'bg-slate-600/20 text-slate-300'"
              >
                {{ store.analysis.real_rate! > 2 ? '高' : store.analysis.real_rate! < 0 ? '负' : '中' }}
              </span>
            </div>
            <p class="text-2xl font-bold text-slate-100">{{ store.analysis.real_rate!.toFixed(2) }}%</p>
            <p class="text-xs text-slate-400 mt-1">
              名义利率: {{ store.analysis.nominal_rate?.toFixed(1) }}% - 通胀率: {{ store.analysis.inflation_rate?.toFixed(1) }}%
            </p>
            <p class="text-xs text-slate-400 mt-2">
              <span v-if="store.analysis.real_rate! > 2">
                📉 实际利率较高可能对黄金形成压力
              </span>
              <span v-else-if="store.analysis.real_rate! < 0">
                📈 负实际利率可能对黄金形成支撑
              </span>
              <span v-else>
                ➡️ 实际利率中性,对黄金影响有限
              </span>
            </p>
          </div>
        </div>
      </section>

      <!-- Explanation -->
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-200 mb-4 flex items-center justify-between">
          <span>市场解读</span>
          <span
            v-if="store.analysis.llm_explanation"
            class="text-xs px-2 py-1 bg-indigo-600/20 text-indigo-300 rounded-md"
          >
            AI 增强
          </span>
        </h2>
        <div
          class="text-slate-300 leading-relaxed prose prose-invert prose-sm max-w-none"
          v-html="formatExplanation(store.analysis.llm_explanation || store.analysis.explanation)"
        ></div>
      </section>

      <!-- Navigation -->
      <div class="flex justify-center gap-4 py-4">
        <router-link to="/chat" class="btn btn-primary">
          询问更多问题 →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import PriceChart from '@/components/PriceChart.vue'

const store = useAnalysisStore()

// News expansion state - track which news items are expanded
const expandedNews = ref<Set<number>>(new Set())

// Price refresh state (for button loading)
const priceRefreshing = ref(false)

// Auto-refresh timer
let priceRefreshTimer: ReturnType<typeof setInterval> | null = null

const toggleNewsExpansion = (index: number) => {
  if (expandedNews.value.has(index)) {
    expandedNews.value.delete(index)
  } else {
    expandedNews.value.add(index)
  }
}

const priceRefreshTime = computed(() => {
  // 优先显示金价刷新时间,否则显示完整刷新时间
  const time = store.priceRefreshTime || store.lastRefresh
  if (!time) return '未更新'
  return time.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
})

const signalLabel = computed(() => {
  const labels: Record<string, string> = {
    strong_buy: '强买',
    buy: '买',
    hold: '观望',
    sell: '卖',
    strong_sell: '强卖',
  }
  return labels[store.analysis?.signal.signal_level || 'hold']
})

const marketStateLabel = computed(() => {
  const labels: Record<string, string> = {
    trend: '趋势模式',
    range: '震荡模式',
    unclear: '不清晰',
  }
  return labels[store.analysis?.market_state || 'unclear']
})

const trendDirectionLabel = computed(() => {
  const labels: Record<string, string> = {
    up: '向上',
    down: '向下',
    neutral: '无方向',
  }
  return labels[store.analysis?.indicators.trend_dir || 'neutral'] || '-'
})

const positionLevelLabel = computed(() => {
  const labels: Record<string, string> = {
    high: '较高仓位',
    medium: '中等仓位',
    low: '低仓位/空仓',
  }
  return labels[store.analysis?.signal.position_level || 'low']
})

const positionLevelClass = computed(() => {
  const level = store.analysis?.signal.position_level
  if (level === 'high') return 'text-emerald-400'
  if (level === 'medium') return 'text-primary'
  return 'text-slate-400'
})

// Helper functions for news
function getSentimentEmoji(sentiment: string): string {
  const emojiMap: Record<string, string> = {
    '利多': '📈',
    '利空': '📉',
    '中性': '➡️',
  }
  return emojiMap[sentiment] || '📊'
}

function getSentimentBadgeClass(sentiment: string): string {
  const classMap: Record<string, string> = {
    '利多': 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    '利空': 'bg-red-500/20 text-red-300 border border-red-500/30',
    '中性': 'bg-slate-500/20 text-slate-300 border border-slate-500/30',
  }
  return classMap[sentiment] || classMap['中性']
}

function formatExplanation(content: string): string {
  // First escape HTML to prevent XSS
  const escaped = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')

  // Then apply markdown formatting
  return escaped
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-100 font-semibold">$1</strong>')
    .replace(/\n/g, '<br>')
}

async function handleRefresh() {
  await store.refreshData(true)
}

// 单独刷新金价（不触发全局分析）
async function handlePriceRefresh() {
  priceRefreshing.value = true
  try {
    await store.fetchPriceOnly()
  } finally {
    priceRefreshing.value = false
  }
}

async function handlePeriodChange(period: string) {
  await store.setAnalysisPeriod(period)
}

// 启动10秒自动刷新
function startPriceAutoRefresh() {
  // 立即执行一次
  store.fetchPriceOnly()

  // 每10秒刷新一次金价
  priceRefreshTimer = setInterval(() => {
    store.fetchPriceOnly()
  }, 10000)  // 10秒
}

// 停止自动刷新
function stopPriceAutoRefresh() {
  if (priceRefreshTimer) {
    clearInterval(priceRefreshTimer)
    priceRefreshTimer = null
  }
}

onMounted(() => {
  store.fetchAnalysis()
  startPriceAutoRefresh()
})

onUnmounted(() => {
  stopPriceAutoRefresh()
})
</script>
