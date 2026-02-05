<template>
  <BaseCard class="market-depth" :padding="padding">
    <!-- 头部 -->
    <div v-if="showHeader" class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold">{{ title }}</h3>
      <div class="flex gap-2">
        <BaseButton
          v-for="level in depthLevels"
          :key="level.value"
          :variant="selectedDepth === level.value ? 'primary' : 'ghost'"
          size="sm"
          @click="handleDepthChange(level.value)"
        >
          {{ level.label }}
        </BaseButton>
      </div>
    </div>

    <!-- 深度图 -->
    <div class="depth-chart-container">
      <canvas ref="chartCanvas" class="depth-canvas"></canvas>

      <!-- 价格标尺 -->
      <div class="price-axis">
        <div
          v-for="(price, index) in priceTicks"
          :key="index"
          class="price-tick"
          :style="{ bottom: `${(index / (priceTicks.length - 1)) * 100}%` }"
        >
          {{ price }}
        </div>
      </div>

      <!-- 当前价格线 -->
      <div
        v-if="showCurrentPriceLine"
        class="current-price-line"
        :style="{ bottom: `${currentPricePercent}%` }"
      >
        <span class="price-label">{{ currentPrice }}</span>
      </div>
    </div>

    <!-- 统计信息 -->
    <div v-if="showStats" class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="text-center">
        <div class="text-text-muted text-xs mb-1">买盘总量</div>
        <div class="font-mono font-semibold text-up">{{ formatNumber(totalBidVolume) }}</div>
      </div>
      <div class="text-center">
        <div class="text-text-muted text-xs mb-1">卖盘总量</div>
        <div class="font-mono font-semibold text-down">{{ formatNumber(totalAskVolume) }}</div>
      </div>
      <div class="text-center">
        <div class="text-text-muted text-xs mb-1">买卖比</div>
        <div class="font-mono font-semibold" :class="bidAskRatioClass">
          {{ bidAskRatio }}
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-background/50 rounded-xl">
      <div class="spinner"></div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

interface DepthData {
  price: number
  bidVolume: number
  askVolume: number
}

interface Props {
  title?: string
  data: DepthData[]
  currentPrice?: number
  loading?: boolean
  showHeader?: boolean
  showStats?: boolean
  showCurrentPriceLine?: boolean
  maxDepth?: number
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  title: '市场深度',
  currentPrice: 0,
  loading: false,
  showHeader: true,
  showStats: true,
  showCurrentPriceLine: true,
  maxDepth: 20,
  padding: 'md',
})

const emit = defineEmits<{
  depthChange: [level: number]
}>()

const chartCanvas = ref<HTMLCanvasElement>()
const selectedDepth = ref(10)

const depthLevels = [
  { label: '10档', value: 10 },
  { label: '20档', value: 20 },
  { label: '50档', value: 50 },
  { label: '全部', value: 100 },
]

// 计算统计数据
const totalBidVolume = computed(() => {
  return props.data.reduce((sum, item) => sum + item.bidVolume, 0)
})

const totalAskVolume = computed(() => {
  return props.data.reduce((sum, item) => sum + item.askVolume, 0)
})

const bidAskRatio = computed(() => {
  if (totalAskVolume.value === 0) return '∞'
  const ratio = totalBidVolume.value / totalAskVolume.value
  return ratio.toFixed(2)
})

const bidAskRatioClass = computed(() => {
  const ratio = totalBidVolume.value / totalAskVolume.value
  if (ratio > 1) return 'text-up'
  if (ratio < 1) return 'text-down'
  return 'text-neutral'
})

// 价格刻度
const priceTicks = computed(() => {
  if (props.data.length === 0) return []
  const prices = props.data.map(d => d.price)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min
  const tickCount = 5

  return Array.from({ length: tickCount }, (_, i) => {
    const price = min + (range * i) / (tickCount - 1)
    return price.toFixed(2)
  })
})

// 当前价格位置百分比
const currentPricePercent = computed(() => {
  if (props.data.length === 0) return 50
  const prices = props.data.map(d => d.price)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min

  if (range === 0) return 50
  return ((props.currentPrice - min) / range) * 100
})

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(2) + 'K'
  return num.toFixed(2)
}

// 处理深度变化
const handleDepthChange = (level: number) => {
  selectedDepth.value = level
  emit('depthChange', level)
}

// 绘制深度图
const drawChart = () => {
  const canvas = chartCanvas.value
  if (!canvas || props.data.length === 0) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 设置画布大小
  const container = canvas.parentElement
  const width = container.clientWidth - 32 // 减去padding
  const height = 200

  canvas.width = width * window.devicePixelRatio
  canvas.height = height * window.devicePixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

  // 清空画布
  ctx.clearRect(0, 0, width, height)

  // 找出最大成交量
  const maxVolume = Math.max(
    ...props.data.map(d => Math.max(d.bidVolume, d.askVolume))
  )

  // 绘制买单 (绿色)
  ctx.fillStyle = 'rgba(38, 166, 154, 0.6)'
  props.data.forEach((item, index) => {
    const barWidth = width / props.data.length
    const x = index * barWidth
    const barHeight = (item.bidVolume / maxVolume) * height * 0.45
    const y = height / 2 - barHeight

    ctx.fillRect(x, y, barWidth - 1, barHeight)
  })

  // 绘制卖单 (红色)
  ctx.fillStyle = 'rgba(239, 83, 80, 0.6)'
  props.data.forEach((item, index) => {
    const barWidth = width / props.data.length
    const x = index * barWidth
    const barHeight = (item.askVolume / maxVolume) * height * 0.45
    const y = height / 2

    ctx.fillRect(x, y, barWidth - 1, barHeight)
  })

  // 绘制中线
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(0, height / 2)
  ctx.lineTo(width, height / 2)
  ctx.stroke()
}

// 监听数据变化
watch(() => props.data, () => {
  drawChart()
}, { deep: true })

onMounted(() => {
  drawChart()

  // 监听窗口大小变化
  window.addEventListener('resize', drawChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', drawChart)
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.market-depth {
  position: relative;
  min-height: 300px;
}

.depth-chart-container {
  position: relative;
  width: 100%;
  min-height: 250px;
  margin: var(--spacing-lg) 0;
}

.depth-canvas {
  width: 100%;
  height: auto;
  display: block;
  border-radius: var(--radius-md);
}

.price-axis {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  pointer-events: none;
  padding: var(--spacing-sm) 0;
  font-family: var(--font-mono);
}

.price-tick {
  transform: translateY(-50%);
  background: rgba(15, 23, 42, 0.8);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast) var(--ease-default);
}

.current-price-line {
  position: absolute;
  left: 0;
  right: 80px;
  height: 1px;
  background: var(--color-primary);
  pointer-events: none;
  transition: all var(--transition-base) var(--ease-default);
  box-shadow: 0 0 8px var(--color-primary);
}

.price-label {
  position: absolute;
  right: 0;
  transform: translateY(-50%) translateX(100%);
  margin-right: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-primary);
  color: #ffffff;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-weight: 600;
  box-shadow: var(--shadow-md);
  white-space: nowrap;
}

/* 统计卡片 */
.grid {
  display: grid;
  gap: var(--spacing-md);
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

/* 加载动画 */
.spinner {
  width: 2rem;
  height: 2rem;
  border: 4px solid var(--color-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 文本样式 */
.text-up {
  color: var(--color-success);
}

.text-down {
  color: var(--color-error);
}

.text-neutral {
  color: var(--color-text-muted);
}

.text-text-muted {
  color: var(--color-text-muted);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-cols-3 {
    grid-template-columns: repeat(1, 1fr);
  }

  .price-axis {
    width: 60px;
    font-size: 10px;
  }

  .current-price-line {
    right: 60px;
  }

  .price-label {
    font-size: 10px;
  }
}
</style>
