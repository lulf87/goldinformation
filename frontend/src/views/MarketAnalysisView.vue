<template>
  <div class="market-analysis-view">
    <!-- Header -->
    <header class="analysis-header">
      <div class="header-container">
        <div class="header-content">
          <div class="header-left">
            <router-link to="/" class="back-link">
              <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </router-link>
            <div class="header-title">
              <h1 class="page-title">深度市场分析</h1>
              <p class="page-subtitle">技术指标 · 趋势分析 · 市场深度</p>
            </div>
          </div>
          <div class="header-actions">
            <router-link
              to="/chat"
              class="cta-button"
            >
              <svg class="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              询问 AI
            </router-link>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div v-if="store.analysis" class="main-content">
      <!-- Technical Indicators Grid -->
      <section class="indicators-grid">
        <!-- MA Indicator -->
        <div class="tech-indicator-card">
          <div class="card-header">
            <h3 class="card-title">移动平均线</h3>
            <svg class="indicator-icon indicator-icon-ma" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div class="card-body">
            <div class="data-row">
              <span class="data-label">MA20</span>
              <span class="data-value" :class="getMAClass(20)">
                {{ getMAValue(20) }}
              </span>
            </div>
            <div class="data-row">
              <span class="data-label">MA60</span>
              <span class="data-value" :class="getMAClass(60)">
                {{ getMAValue(60) }}
              </span>
            </div>
            <div class="data-row">
              <span class="data-label">MA200</span>
              <span class="data-value" :class="getMAClass(200)">
                {{ getMAValue(200) }}
              </span>
            </div>
          </div>
          <div class="card-footer">
            <p class="trend-text" :class="getMATrendClass()">
              {{ getMATrendText() }}
            </p>
          </div>
        </div>

        <!-- RSI Indicator -->
        <div class="tech-indicator-card">
          <div class="card-header">
            <h3 class="card-title">RSI 指标</h3>
            <svg class="indicator-icon indicator-icon-rsi" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="rsi-display">
            <p class="rsi-value" :class="getRSIClass()">
              {{ getRSIValue() }}
            </p>
            <p class="rsi-label">RSI (14)</p>
          </div>
          <div class="rsi-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="getRSIBarClass()"
                :style="{ width: `${Math.min(getRSIValue(), 100)}%` }"
              ></div>
            </div>
            <p class="progress-text" :class="getRSITextClass()">
              {{ getRSIText() }}
            </p>
          </div>
        </div>

        <!-- ATR Indicator -->
        <div class="tech-indicator-card">
          <div class="card-header">
            <h3 class="card-title">ATR 波动率</h3>
            <svg class="indicator-icon indicator-icon-atr" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
            </svg>
          </div>
          <div class="atr-display">
            <p class="atr-value">
              {{ getATRValue() }}
            </p>
            <p class="atr-label">平均真实波幅</p>
          </div>
          <div class="card-footer">
            <p class="trend-text" :class="getATRClass()">
              {{ getATRText() }}
            </p>
          </div>
        </div>

        <!-- Bollinger Bands -->
        <div class="tech-indicator-card">
          <div class="card-header">
            <h3 class="card-title">布林带</h3>
            <svg class="indicator-icon indicator-icon-bb" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="card-body">
            <div class="data-row">
              <span class="data-label">上轨</span>
              <span class="data-value text-red">
                {{ getBBValue('upper') }}
              </span>
            </div>
            <div class="data-row">
              <span class="data-label">中轨</span>
              <span class="data-value text-neutral">
                {{ getBBValue('middle') }}
              </span>
            </div>
            <div class="data-row">
              <span class="data-label">下轨</span>
              <span class="data-value text-emerald">
                {{ getBBValue('lower') }}
              </span>
            </div>
          </div>
          <div class="card-footer">
            <p class="trend-text" :class="getBBPositionClass()">
              {{ getBBPositionText() }}
            </p>
          </div>
        </div>
      </section>

      <!-- Trend Analysis -->
      <section class="trend-section">
        <h2 class="section-title">
          <svg class="section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          趋势分析
        </h2>
        <div class="trend-grid">
          <div class="trend-card">
            <p class="trend-label">短期趋势 (5日)</p>
            <div class="trend-value">
              <svg class="trend-icon" :class="getTrendIconClass('short')" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <span class="trend-text" :class="getTrendTextClass('short')">
                {{ getTrendText('short') }}
              </span>
            </div>
          </div>
          <div class="trend-card">
            <p class="trend-label">中期趋势 (20日)</p>
            <div class="trend-value">
              <svg class="trend-icon" :class="getTrendIconClass('medium')" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <span class="trend-text" :class="getTrendTextClass('medium')">
                {{ getTrendText('medium') }}
              </span>
            </div>
          </div>
          <div class="trend-card">
            <p class="trend-label">长期趋势 (60日)</p>
            <div class="trend-value">
              <svg class="trend-icon" :class="getTrendIconClass('long')" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <span class="trend-text" :class="getTrendTextClass('long')">
                {{ getTrendText('long') }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Market Depth Visualization -->
      <section class="depth-section">
        <h2 class="section-title">
          <svg class="section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          市场深度分析
        </h2>
        <MarketDepth />
      </section>

      <!-- Support & Resistance -->
      <section class="levels-section">
        <h2 class="section-title">
          <svg class="section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          支撑与阻力
        </h2>
        <div class="levels-grid">
          <!-- Support Levels -->
          <div class="levels-column">
            <h3 class="levels-title levels-title-support">支撑位</h3>
            <div class="levels-list">
              <div
                v-for="(level, index) in getSupportLevels()"
                :key="`support-${index}`"
                class="level-item level-item-support"
              >
                <span class="level-label">支撑 {{ index + 1 }}</span>
                <span class="level-value">{{ level }}</span>
              </div>
            </div>
          </div>
          <!-- Resistance Levels -->
          <div class="levels-column">
            <h3 class="levels-title levels-title-resistance">阻力位</h3>
            <div class="levels-list">
              <div
                v-for="(level, index) in getResistanceLevels()"
                :key="`resistance-${index}`"
                class="level-item level-item-resistance"
              >
                <span class="level-label">阻力 {{ index + 1 }}</span>
                <span class="level-value">{{ level }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Volume Analysis -->
      <section class="volume-section">
        <h2 class="section-title">
          <svg class="section-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          成交量分析
        </h2>
        <div class="volume-grid">
          <div class="volume-card">
            <p class="volume-label">成交量</p>
            <p class="volume-value volume-value-neutral">{{ getVolumeValue() }}</p>
          </div>
          <div class="volume-card">
            <p class="volume-label">成交量变化</p>
            <p class="volume-value" :class="getVolumeChangeClass()">
              {{ getVolumeChange() }}
            </p>
          </div>
          <div class="volume-card">
            <p class="volume-label">量能状态</p>
            <p class="volume-value" :class="getVolumeStatusClass()">
              {{ getVolumeStatus() }}
            </p>
          </div>
        </div>
      </section>
    </div>

    <!-- Loading State -->
    <div v-else class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在加载分析数据...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import MarketDepth from '@/components/MarketDepth.vue'

const store = useAnalysisStore()

// MA Indicator Helpers
function getMAValue(period: number): string {
  const currentPrice = store.analysis?.current_price || 0
  // 简化计算 - 实际应从 API 获取
  const maValues: Record<number, number> = {
    20: currentPrice * 0.998,
    60: currentPrice * 0.995,
    200: currentPrice * 0.990
  }
  return (maValues[period] || currentPrice).toFixed(2)
}

function getMAClass(period: number): string {
  const currentPrice = store.analysis?.current_price || 0
  const ma = parseFloat(getMAValue(period))
  return currentPrice > ma ? 'text-emerald' : 'text-red'
}

function getMATrendText(): string {
  const ma20 = parseFloat(getMAValue(20))
  const ma60 = parseFloat(getMAValue(60))
  const currentPrice = store.analysis?.current_price || 0

  if (currentPrice > ma20 && ma20 > ma60) {
    return '多头排列，强势上涨'
  } else if (currentPrice < ma20 && ma20 < ma60) {
    return '空头排列，弱势下跌'
  } else {
    return '交织状态，方向不明'
  }
}

function getMATrendClass(): string {
  const ma20 = parseFloat(getMAValue(20))
  const ma60 = parseFloat(getMAValue(60))
  const currentPrice = store.analysis?.current_price || 0

  if (currentPrice > ma20 && ma20 > ma60) {
    return 'text-emerald'
  } else if (currentPrice < ma20 && ma20 < ma60) {
    return 'text-red'
  } else {
    return 'text-muted'
  }
}

// RSI Indicator Helpers
function getRSIValue(): number {
  // 简化计算 - 实际应从 API 获取
  return Math.floor(Math.random() * 100)
}

function getRSIClass(): string {
  const rsi = getRSIValue()
  if (rsi >= 70) return 'text-red'
  if (rsi <= 30) return 'text-emerald'
  return 'text-neutral'
}

function getRSIBarClass(): string {
  const rsi = getRSIValue()
  if (rsi >= 70) return 'progress-fill-red'
  if (rsi <= 30) return 'progress-fill-emerald'
  return 'progress-fill-neutral'
}

function getRSIText(): string {
  const rsi = getRSIValue()
  if (rsi >= 70) return '超买区域'
  if (rsi <= 30) return '超卖区域'
  if (rsi >= 50) return '偏多'
  return '偏空'
}

function getRSITextClass(): string {
  const rsi = getRSIValue()
  if (rsi >= 70) return 'text-red'
  if (rsi <= 30) return 'text-emerald'
  return 'text-muted'
}

// ATR Indicator Helpers
function getATRValue(): string {
  const currentPrice = store.analysis?.current_price || 2000
  const atr = currentPrice * 0.015
  return atr.toFixed(2)
}

function getATRClass(): string {
  const currentPrice = store.analysis?.current_price || 2000
  const atr = parseFloat(getATRValue())
  const atrPercent = (atr / currentPrice) * 100

  if (atrPercent > 2) return 'text-red'
  if (atrPercent < 0.5) return 'text-emerald'
  return 'text-muted'
}

function getATRText(): string {
  const currentPrice = store.analysis?.current_price || 2000
  const atr = parseFloat(getATRValue())
  const atrPercent = (atr / currentPrice) * 100

  if (atrPercent > 2) return '高波动率'
  if (atrPercent < 0.5) return '低波动率'
  return '正常波动率'
}

// Bollinger Bands Helpers
function getBBValue(position: 'upper' | 'middle' | 'lower'): string {
  const currentPrice = store.analysis?.current_price || 2000
  const atr = parseFloat(getATRValue())

  const values = {
    upper: (currentPrice + atr * 2).toFixed(2),
    middle: currentPrice.toFixed(2),
    lower: (currentPrice - atr * 2).toFixed(2)
  }

  return values[position]
}

function getBBPositionText(): string {
  const currentPrice = store.analysis?.current_price || 2000
  const upper = parseFloat(getBBValue('upper'))
  const lower = parseFloat(getBBValue('lower'))
  const middle = parseFloat(getBBValue('middle'))

  if (currentPrice > (upper + middle) / 2) {
    return '价格接近上轨，可能回调'
  } else if (currentPrice < (lower + middle) / 2) {
    return '价格接近下轨，可能反弹'
  } else {
    return '价格在中轨附近，震荡'
  }
}

function getBBPositionClass(): string {
  const currentPrice = store.analysis?.current_price || 2000
  const upper = parseFloat(getBBValue('upper'))
  const lower = parseFloat(getBBValue('lower'))
  const middle = parseFloat(getBBValue('middle'))

  if (currentPrice > (upper + middle) / 2) {
    return 'text-red'
  } else if (currentPrice < (lower + middle) / 2) {
    return 'text-emerald'
  } else {
    return 'text-muted'
  }
}

// Trend Analysis Helpers
function getTrendText(period: 'short' | 'medium' | 'long'): string {
  const trends = {
    short: ['强势上涨', '温和上涨', '震荡', '温和下跌', '强势下跌'],
    medium: ['上升趋势', '震荡上行', '区间震荡', '震荡下行', '下降趋势'],
    long: ['牛市', '偏多', '中性', '偏空', '熊市']
  }

  const index = Math.floor(Math.random() * 5)
  return trends[period][index]
}

function getTrendIconClass(period: 'short' | 'medium' | 'long'): string {
  const text = getTrendText(period)
  if (text.includes('上涨') || text.includes('升') || text.includes('牛') || text.includes('多')) {
    return 'text-emerald'
  } else if (text.includes('下跌') || text.includes('降') || text.includes('熊') || text.includes('空')) {
    return 'text-red'
  } else {
    return 'text-muted'
  }
}

function getTrendTextClass(period: 'short' | 'medium' | 'long'): string {
  return getTrendIconClass(period)
}

// Support & Resistance Levels
function getSupportLevels(): string[] {
  const currentPrice = store.analysis?.current_price || 2000
  return [
    (currentPrice * 0.990).toFixed(2),
    (currentPrice * 0.980).toFixed(2),
    (currentPrice * 0.965).toFixed(2)
  ]
}

function getResistanceLevels(): string[] {
  const currentPrice = store.analysis?.current_price || 2000
  return [
    (currentPrice * 1.010).toFixed(2),
    (currentPrice * 1.020).toFixed(2),
    (currentPrice * 1.035).toFixed(2)
  ]
}

// Volume Analysis
function getVolumeValue(): string {
  // 模拟成交量数据
  const volume = Math.floor(Math.random() * 1000000) + 500000
  return (volume / 10000).toFixed(2) + '万'
}

function getVolumeChange(): string {
  const change = (Math.random() * 40 - 20).toFixed(1)
  return (parseFloat(change) > 0 ? '+' : '') + change + '%'
}

function getVolumeChangeClass(): string {
  const change = parseFloat(getVolumeChange())
  return change > 0 ? 'text-emerald' : 'text-red'
}

function getVolumeStatus(): string {
  const change = parseFloat(getVolumeChange())
  if (change > 20) return '放量'
  if (change < -20) return '缩量'
  return '平稳'
}

function getVolumeStatusClass(): string {
  const status = getVolumeStatus()
  if (status === '放量') return 'text-red'
  if (status === '缩量') return 'text-emerald'
  return 'text-muted'
}

onMounted(() => {
  store.fetchAnalysis()
})
</script>

<style scoped>
/* Page Layout */
.market-analysis-view {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}

/* Header */
.analysis-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-backdrop);
  border-bottom: 1px solid var(--color-border);
}

.header-container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--spacing-md) var(--spacing-lg);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.back-link {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  transition: color var(--transition-base) var(--ease-default);
}

.back-link:hover {
  color: var(--color-text);
}

.back-icon {
  width: var(--icon-md);
  height: var(--icon-md);
}

.header-title {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.cta-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--transition-base) var(--ease-default);
  text-decoration: none;
}

.cta-button:hover {
  background: var(--color-primary-hover);
}

.button-icon {
  width: var(--icon-sm);
  height: var(--icon-sm);
}

/* Main Content */
.main-content {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* Indicators Grid */
.indicators-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .indicators-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .indicators-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Tech Indicator Card */
.tech-indicator-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  transition: all var(--transition-base) var(--ease-default);
  display: flex;
  flex-direction: column;
}

.tech-indicator-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--glow-primary), var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.card-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin: 0;
}

.indicator-icon {
  width: var(--icon-sm);
  height: var(--icon-sm);
}

.indicator-icon-ma {
  color: #3B82F6;
}

.indicator-icon-rsi {
  color: #8B5CF6;
}

.indicator-icon-atr {
  color: #F59E0B;
}

.indicator-icon-bb {
  color: #10B981;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.data-value {
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  font-weight: 600;
}

.text-emerald {
  color: var(--color-success);
}

.text-red {
  color: var(--color-error);
}

.text-neutral {
  color: var(--color-text-secondary);
}

.text-muted {
  color: var(--color-text-muted);
}

.card-footer {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.trend-text {
  font-size: var(--text-xs);
  margin: 0;
}

/* RSI Display */
.rsi-display {
  text-align: center;
  padding: var(--spacing-md) 0;
}

.rsi-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  font-family: var(--font-mono);
  margin: 0;
}

.rsi-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: var(--spacing-sm) 0 0 0;
}

.rsi-progress {
  margin-top: var(--spacing-md);
}

.progress-bar {
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: all var(--transition-slow) var(--ease-default);
}

.progress-fill-red {
  background: var(--color-error);
}

.progress-fill-emerald {
  background: var(--color-success);
}

.progress-fill-neutral {
  background: var(--color-text-muted);
}

.progress-text {
  font-size: var(--text-xs);
  margin-top: var(--spacing-sm);
  margin-bottom: 0;
}

/* ATR Display */
.atr-display {
  text-align: center;
  padding: var(--spacing-md) 0;
}

.atr-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
  margin: 0;
}

.atr-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: var(--spacing-sm) 0 0 0;
}

/* Section */
.trend-section,
.depth-section,
.levels-section,
.volume-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--spacing-md) 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.section-icon {
  width: var(--icon-md);
  height: var(--icon-md);
}

/* Trend Grid */
.trend-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .trend-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.trend-card {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-base) var(--ease-default);
}

.trend-card:hover {
  background: var(--glass-bg);
  border-color: var(--color-primary);
}

.trend-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0 0 var(--spacing-sm) 0;
}

.trend-value {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.trend-icon {
  width: var(--icon-lg);
  height: var(--icon-lg);
}

.trend-text {
  font-size: var(--text-xl);
  font-weight: 700;
}

/* Levels Grid */
.levels-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-lg);
}

@media (min-width: 768px) {
  .levels-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.levels-title {
  font-size: var(--text-sm);
  font-weight: 500;
  margin: 0 0 var(--spacing-md) 0;
}

.levels-title-support {
  color: var(--color-success);
}

.levels-title-resistance {
  color: var(--color-error);
}

.levels-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.level-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid;
}

.level-item-support {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.level-item-resistance {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.level-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.level-value {
  font-size: var(--text-lg);
  font-family: var(--font-mono);
  font-weight: 600;
}

.level-item-support .level-value {
  color: var(--color-success);
}

.level-item-resistance .level-value {
  color: var(--color-error);
}

/* Volume Grid */
.volume-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .volume-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.volume-card {
  text-align: center;
  padding: var(--spacing-md);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
}

.volume-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0 0 var(--spacing-sm) 0;
}

.volume-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin: 0;
}

.volume-value-neutral {
  color: var(--color-text-secondary);
}

/* Loading State */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 24rem;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto var(--spacing-lg) auto;
}

.loading-spinner::before {
  content: '';
  position: absolute;
  inset: 0;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-radius: 50%;
}

.loading-spinner::after {
  content: '';
  position: absolute;
  inset: 0;
  border: 4px solid transparent;
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: var(--color-text-muted);
  font-size: var(--text-lg);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .header-container {
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .main-content {
    padding: var(--spacing-md) var(--spacing-sm);
  }

  .tech-indicator-card {
    padding: var(--spacing-md);
  }

  .trend-card {
    padding: var(--spacing-sm);
  }

  .page-title {
    font-size: var(--text-xl);
  }
}
</style>
