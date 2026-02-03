import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiAnalysis, type MarketAnalysis } from '@/api'

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const analysis = ref<MarketAnalysis | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastRefresh = ref<Date | null>(null)
  const priceRefreshTime = ref<Date | null>(null)  // 金价刷新时间(来自后端)
  const priceRefreshTimer = ref<ReturnType<typeof setInterval> | null>(null)
  const analysisPeriod = ref('1y')

  // Computed
  const signalLevelClass = computed(() => {
    if (!analysis.value) return ''
    return `signal-${analysis.value.signal.signal_level}`
  })

  const priceChangeClass = computed(() => {
    if (!analysis.value) return ''
    return analysis.value.price_change >= 0 ? 'text-emerald-400' : 'text-red-400'
  })

  const priceChangeSign = computed(() => {
    if (!analysis.value) return ''
    return analysis.value.price_change >= 0 ? '+' : ''
  })

  // Actions
  function getInterval(period: string) {
    const map: Record<string, string> = {
      '1d': '1m',
      '1mo': '1d',
      '1y': '1wk',
      '5y': '1mo',
      'max': '1mo',
    }
    return map[period] || '1d'
  }

  async function fetchAnalysis(period = analysisPeriod.value) {
    loading.value = true
    error.value = null
    try {
      analysis.value = await apiAnalysis.getAnalysis(period, getInterval(period))
      lastRefresh.value = new Date()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch analysis'
      console.error('Error fetching analysis:', e)
    } finally {
      loading.value = false
    }
  }

  async function refreshData(force = false) {
    loading.value = true
    error.value = null
    try {
      await apiAnalysis.refreshData(force)
      await fetchAnalysis()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to refresh data'
    } finally {
      loading.value = false
    }
  }

  async function fetchPriceOnly() {
    try {
      const priceData = await apiAnalysis.getPrice()
      if (priceData.success && analysis.value) {
        // 更新当前价格
        analysis.value.current_price = priceData.current_price
        analysis.value.price_change = priceData.price_change
        analysis.value.price_change_pct = priceData.price_change_pct
        // 更新金价刷新时间(来自后端)
        priceRefreshTime.value = new Date(priceData.price_refresh_time)
      }
    } catch (e) {
      console.error('Error fetching price:', e)
    }
  }

  function startPriceAutoRefresh() {
    if (priceRefreshTimer.value) return
    priceRefreshTimer.value = setInterval(() => {
      fetchPriceOnly()
    }, 10000)
  }

  function stopPriceAutoRefresh() {
    if (priceRefreshTimer.value) {
      clearInterval(priceRefreshTimer.value)
      priceRefreshTimer.value = null
    }
  }

  async function setAnalysisPeriod(period: string) {
    if (analysisPeriod.value === period) return
    analysisPeriod.value = period
    await fetchAnalysis(period)
  }

  function formatExplanation(explanation: string) {
    // Convert markdown-style bold to HTML
    return explanation
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-200">$1</strong>')
      .replace(/\n/g, '<br>')
  }

  return {
    // State
    analysis,
    loading,
    error,
    lastRefresh,
    priceRefreshTime,
    analysisPeriod,
    // Computed
    signalLevelClass,
    priceChangeClass,
    priceChangeSign,
    // Actions
    fetchAnalysis,
    refreshData,
    fetchPriceOnly,
    startPriceAutoRefresh,
    stopPriceAutoRefresh,
    setAnalysisPeriod,
    formatExplanation,
  }
})
