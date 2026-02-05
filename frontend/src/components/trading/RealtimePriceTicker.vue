<template>
  <div class="realtime-price-ticker" :class="variant">
    <!-- 标题 -->
    <div v-if="showLabel" class="ticker-label">
      <slot name="label">
        <span class="text-sm font-medium text-text-muted">{{ label }}</span>
      </slot>
    </div>

    <!-- 跑马灯容器 -->
    <div class="ticker-container">
      <div
        class="ticker-content"
        :class="{ 'animate-marquee': pauseOnHover }"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
      >
        <div
          v-for="(item, index) in duplicatedItems"
          :key="index"
          class="ticker-item"
          @click="handleItemClick(item)"
        >
          <!-- 名称 -->
          <span class="ticker-symbol">{{ item.symbol }}</span>

          <!-- 价格 -->
          <span class="ticker-price font-mono" :class="getTrendClass(item)">
            {{ formatPrice(item.price) }}
          </span>

          <!-- 涨跌幅 -->
          <span class="ticker-change font-mono" :class="getTrendClass(item)">
            {{ formatChange(item) }}
          </span>

          <!-- 时间 -->
          <span v-if="showTime" class="ticker-time text-text-muted text-xs">
            {{ item.time }}
          </span>
        </div>
      </div>
    </div>

    <!-- 分隔线 -->
    <div v-if="showDivider" class="ticker-divider"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface PriceItem {
  symbol: string
  price: number
  change?: number
  changePercent?: number
  time?: string
  currency?: string
}

interface Props {
  items: PriceItem[]
  label?: string
  variant?: 'horizontal' | 'vertical'
  showLabel?: boolean
  showTime?: boolean
  showDivider?: boolean
  pauseOnHover?: boolean
  speed?: 'slow' | 'normal' | 'fast'
  itemGap?: string
}

const props = withDefaults(defineProps<Props>(), {
  label: '实时行情',
  variant: 'horizontal',
  showLabel: true,
  showTime: false,
  showDivider: true,
  pauseOnHover: true,
  speed: 'normal',
  itemGap: '2rem',
})

const emit = defineEmits<{
  itemClick: [item: PriceItem]
}>()

const isPaused = ref(false)

// 复制数组以实现无缝滚动
const duplicatedItems = computed(() => {
  // 至少复制两次以填满屏幕
  const items = [...props.items, ...props.items, ...props.items]
  return items
})

// 获取趋势类
const getTrendClass = (item: PriceItem) => {
  const change = item.changePercent ?? item.change ?? 0
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-neutral'
}

// 格式化价格
const formatPrice = (price: number) => {
  const currency = props.items[0]?.currency || '¥'
  return `${currency}${price.toFixed(2)}`
}

// 格式化涨跌
const formatChange = (item: PriceItem) => {
  const change = item.changePercent ?? item.change
  if (change === undefined || change === null) return '-'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

// 处理鼠标进入
const handleMouseEnter = () => {
  if (props.pauseOnHover) {
    isPaused.value = true
  }
}

// 处理鼠标离开
const handleMouseLeave = () => {
  isPaused.value = false
}

// 处理项目点击
const handleClick = (item: PriceItem) => {
  emit('itemClick', item)
}
</script>

<style scoped>
.realtime-price-ticker {
  @apply relative;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.ticker-label {
  @apply flex-shrink-0;
}

.ticker-container {
  @apply flex-1 overflow-hidden;
}

.ticker-content {
  @apply flex items-center;
  white-space: nowrap;
}

.ticker-content.animate-marquee:not(:hover) {
  animation: marquee var(--marquee-duration, 30s) linear infinite;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-33.33%);
  }
}

.ticker-item {
  @apply inline-flex items-center gap-3 px-4 py-2 cursor-pointer transition-colors duration-200;
  @apply hover:bg-background/50 rounded;
}

.ticker-symbol {
  @apply font-medium text-text;
}

.ticker-price {
  @apply font-semibold;
}

.ticker-divider {
  @apply w-px h-6 bg-gray-200 dark:bg-gray-700 flex-shrink-0;
}

/* 响应式 */
@media (max-width: 768px) {
  .ticker-item {
    @apply gap-2 px-3 py-1;
  }

  .ticker-symbol {
    @apply text-sm;
  }

  .ticker-price {
    @apply text-base;
  }
}

/* 不同速度 */
.realtime-price-ticker[data-speed="slow"] .ticker-content {
  --marquee-duration: 60s;
}

.realtime-price-ticker[data-speed="normal"] .ticker-content {
  --marquee-duration: 30s;
}

.realtime-price-ticker[data-speed="fast"] .ticker-content {
  --marquee-duration: 15s;
}
</style>
