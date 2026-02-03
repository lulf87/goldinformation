<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-slate-200">价格趋势与关键位</h2>
      <!-- 周期切换按钮 -->
      <div class="flex gap-2">
        <button
          v-for="p in periods"
          :key="p.value"
          @click="selectPeriod(p.value)"
          :class="[
            'px-3 py-1 text-xs rounded transition-colors',
            currentPeriod === p.value
              ? 'bg-primary text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          ]"
        >
          {{ p.label }}
        </button>
      </div>
    </div>
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-400">{{ error }}</p>
    </div>
    <v-chart
      v-else
      :option="chartOption"
      :autoresize="true"
      class="w-full"
      style="height: 400px"
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
