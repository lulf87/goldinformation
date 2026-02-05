<template>
  <div class="price-chart-card">
    <div class="chart-header">
      <h2 class="chart-title">价格趋势与关键位</h2>
      <!-- 周期切换按钮 -->
      <div class="period-buttons">
        <button
          v-for="p in periods"
          :key="p.value"
          @click="selectPeriod(p.value)"
          :class="[
            'period-button',
            currentPeriod === p.value ? 'period-button-active' : 'period-button-inactive'
          ]"
        >
          {{ p.label }}
        </button>
      </div>
    </div>
    <div v-if="loading" class="chart-loading">
      <div class="loading-spinner"></div>
    </div>
    <div v-else-if="error" class="chart-error">
      <p class="error-text">{{ error }}</p>
    </div>
    <v-chart
      v-else
      :option="chartOption"
      :autoresize="true"
      class="chart-container"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  MarkLineComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'
import type { ChartData } from '@/api'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  MarkLineComponent,
])

interface Props {
  symbol?: string
  period?: string
}

const props = withDefaults(defineProps<Props>(), {
  symbol: 'GC=F',
  period: '1y',
})

const emit = defineEmits<{
  (e: 'update:period', value: string): void
}>()

// 周期选项
const periods = [
  { label: '分', value: '1d' },
  { label: '日', value: '1mo' },
  { label: '周', value: '1y' },
  { label: '月', value: '5y' },
  { label: '年', value: 'max' },
]

const currentPeriod = ref(props.period)
const loading = ref(true)
const error = ref<string | null>(null)
const chartData = ref<ChartData | null>(null)

// 选择周期
function selectPeriod(period: string) {
  if (currentPeriod.value !== period) {
    currentPeriod.value = period
    emit('update:period', period)
    loadChartData()
  }
}

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

const chartOption = computed<EChartsOption>(() => {
  if (!chartData.value) return {}

  const dates = chartData.value.data.map((d) => d.date)
  const prices = chartData.value.data.map((d) => d.price)
  const maShort = chartData.value.data.map((d) => d.ma_short ?? null)
  const maMid = chartData.value.data.map((d) => d.ma_mid ?? null)

  // Prepare mark lines for key levels
  const markLines: any[] = []

  if (chartData.value.key_levels.support) {
    markLines.push({
      name: '支撑位',
      yAxis: chartData.value.key_levels.support,
      line: { type: 'solid', color: '#10b981', width: 2 },
      label: { formatter: '支撑: {c}', position: 'end' },
    })
  }

  if (chartData.value.key_levels.resistance) {
    markLines.push({
      name: '阻力位',
      yAxis: chartData.value.key_levels.resistance,
      line: { type: 'solid', color: '#ef4444', width: 2 },
      label: { formatter: '阻力: {c}', position: 'end' },
    })
  }

  if (chartData.value.key_levels.range_high) {
    markLines.push({
      name: '区间上沿',
      yAxis: chartData.value.key_levels.range_high,
      line: { type: 'dashed', color: '#f59e0b', width: 1 },
      label: { formatter: '区间上: {c}', position: 'end' },
    })
  }

  if (chartData.value.key_levels.range_low) {
    markLines.push({
      name: '区间下沿',
      yAxis: chartData.value.key_levels.range_low,
      line: { type: 'dashed', color: '#f59e0b', width: 1 },
      label: { formatter: '区间下: {c}', position: 'end' },
    })
  }

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: ['价格', 'MA20', 'MA60'],
      textStyle: { color: '#cbd5e1' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8', formatter: '${value}' },
      splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
    },
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        showSymbol: false,
        itemStyle: { color: '#3b82f6' },
        markLine: {
          data: markLines,
          symbol: 'none',
        },
      },
      {
        name: 'MA20',
        type: 'line',
        data: maShort,
        smooth: true,
        showSymbol: false,
        itemStyle: { color: '#10b981' },
      },
      {
        name: 'MA60',
        type: 'line',
        data: maMid,
        smooth: true,
        showSymbol: false,
        itemStyle: { color: '#f59e0b' },
      },
    ],
  }
})

async function loadChartData() {
  loading.value = true
  error.value = null

  try {
    const { apiAnalysis } = await import('@/api')
    chartData.value = await apiAnalysis.getChartData(
      props.symbol,
      currentPeriod.value,
      getInterval(currentPeriod.value)
    )
  } catch (e) {
    console.error('Failed to load chart data:', e)
    error.value = '加载图表数据失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadChartData()
})

watch(
  () => props.period,
  (newPeriod) => {
    if (newPeriod && newPeriod !== currentPeriod.value) {
      currentPeriod.value = newPeriod
      loadChartData()
    }
  }
)
</script>

<style scoped>
/* Card */
.price-chart-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

/* Header */
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.chart-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
}

.period-buttons {
  display: flex;
  gap: var(--spacing-sm);
}

.period-button {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  transition: all var(--transition-base) var(--ease-default);
}

.period-button-active {
  background: var(--color-primary);
  color: white;
}

.period-button-active:hover {
  background: var(--color-primary-hover);
}

.period-button-inactive {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}

.period-button-inactive:hover {
  background: var(--color-border);
}

/* Loading State */
.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 24rem;
}

.loading-spinner {
  position: relative;
  width: 48px;
  height: 48px;
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

/* Error State */
.chart-error {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.error-text {
  color: var(--color-error);
  margin: 0;
}

/* Chart Container */
.chart-container {
  width: 100%;
  height: 400px;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .period-buttons {
    width: 100%;
    justify-content: space-between;
  }

  .period-button {
    flex: 1;
    padding: var(--spacing-xs);
  }

  .chart-container {
    height: 300px;
  }
}
</style>
