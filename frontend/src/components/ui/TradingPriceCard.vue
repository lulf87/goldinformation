<template>
  <BaseCard
    :variant="variant"
    :hoverable="hoverable"
    :padding="padding"
    :shadow="shadow"
    class="trading-price-card"
    @click="handleClick"
  >
    <!-- 头部: 标题和标签 -->
    <div v-if="showHeader" class="flex justify-between items-start mb-4">
      <div class="flex items-center gap-2">
        <h3 class="text-lg font-semibold">{{ title }}</h3>
        <span v-if="symbol" class="badge badge-info text-xs">{{ symbol }}</span>
      </div>

      <!-- 趋势图标 -->
      <div v-if="showTrendIcon" class="trend-icon" :class="trendClass">
        <svg v-if="isUp" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        <svg v-else-if="isDown" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14" />
        </svg>
      </div>
    </div>

    <!-- 主要价格 -->
    <div class="price-section mb-4">
      <div class="flex items-baseline gap-2">
        <span class="text-3xl font-bold font-mono">{{ formattedPrice }}</span>
        <span v-if="currency" class="text-text-muted text-sm">{{ currency }}</span>
      </div>

      <!-- 涨跌幅 -->
      <div v-if="change !== null || changePercent !== null" class="flex items-center gap-3 mt-2">
        <span v-if="change !== null" class="font-mono" :class="trendClass">
          {{ change >= 0 ? '+' : '' }}{{ formattedChange }}
        </span>
        <span v-if="changePercent !== null" class="font-mono" :class="trendClass">
          {{ changePercent >= 0 ? '+' : '' }}{{ changePercent }}%
        </span>
      </div>
    </div>

    <!-- 数据列表 -->
    <div v-if="dataList && dataList.length > 0" class="data-list space-y-2">
      <div
        v-for="(item, index) in dataList"
        :key="index"
        class="flex justify-between items-center text-sm"
      >
        <span class="text-text-muted">{{ item.label }}</span>
        <span class="font-mono font-medium">{{ item.value }}</span>
      </div>
    </div>

    <!-- 进度条 (可选) -->
    <div v-if="showProgress && progress !== null" class="mt-4">
      <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          class="h-full transition-all duration-300"
          :class="progressClass"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>

    <!-- 底部插槽 -->
    <div v-if="$slots.footer" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <slot name="footer" />
    </div>

    <!-- 加载中状态 -->
    <div v-if="loading" class="absolute inset-0 bg-white/50 dark:bg-background/50 backdrop-blur-sm rounded-xl flex items-center justify-center">
      <div class="spinner"></div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseCard from './BaseCard.vue'

interface DataItem {
  label: string
  value: string | number
}

interface Props {
  title: string
  symbol?: string
  price: number
  currency?: string
  change?: number | null
  changePercent?: number | null
  dataList?: DataItem[]
  showHeader?: boolean
  showTrendIcon?: boolean
  showProgress?: boolean
  progress?: number | null
  loading?: boolean
  hoverable?: boolean
  variant?: 'default' | 'glass' | 'bordered'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  currency: '¥',
  change: null,
  changePercent: null,
  dataList: () => [],
  showHeader: true,
  showTrendIcon: true,
  showProgress: false,
  progress: null,
  loading: false,
  hoverable: false,
  variant: 'default',
  padding: 'md',
  shadow: 'md',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const isUp = computed(() => (props.changePercent ?? 0) > 0 || (props.change ?? 0) > 0)
const isDown = computed(() => (props.changePercent ?? 0) < 0 || (props.change ?? 0) < 0)

const trendClass = computed(() => {
  if (isUp.value) return 'text-up'
  if (isDown.value) return 'text-down'
  return 'text-neutral'
})

const progressClass = computed(() => {
  if (isUp.value) return 'bg-trading-up'
  if (isDown.value) return 'bg-trading-down'
  return 'bg-gray-400'
})

const formattedPrice = computed(() => {
  const price = props.price ?? 0
  return typeof price === 'number' ? price.toFixed(2) : '0.00'
})

const formattedChange = computed(() => {
  if (props.change === null || props.change === undefined) return ''
  return typeof props.change === 'number' ? props.change.toFixed(2) : '0.00'
})

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style scoped>
/* 涨跌颜色类 */
.text-up {
  color: #26A69A;
}

.text-down {
  color: #EF5350;
}

.text-neutral {
  color: #94A3B8;
}

.trading-price-card {
  @apply relative;
}

.price-section {
  @apply relative;
}

.data-list {
  @apply border-t border-gray-200 dark:border-gray-700 pt-4;
}

.trend-icon {
  @apply p-1 rounded-full;
}

.trend-icon.text-up {
  @apply bg-green-100 dark:bg-green-900;
  color: #26A69A;
}

.trend-icon.text-down {
  @apply bg-red-100 dark:bg-red-900;
  color: #EF5350;
}

.trend-icon.text-neutral {
  @apply bg-gray-100 dark:bg-gray-800;
  color: #94A3B8;
}

.spinner {
  @apply w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin;
}
</style>
