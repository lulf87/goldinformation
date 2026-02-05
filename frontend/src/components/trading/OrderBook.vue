<template>
  <BaseCard class="order-book" :padding="padding">
    <!-- 头部 -->
    <div v-if="showHeader" class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold">{{ title }}</h3>
      <BaseButton size="sm" variant="ghost" @click="handleRefresh">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </BaseButton>
    </div>

    <!-- 当前价格 -->
    <div v-if="showCurrentPrice" class="current-price mb-4 p-3 bg-background rounded-lg">
      <div class="flex justify-between items-center">
        <span class="text-text-muted text-sm">当前价格</span>
        <div class="text-right">
          <div class="text-2xl font-bold font-mono" :class="priceTrendClass">
            {{ currentPrice }}
          </div>
          <div class="text-sm" :class="priceTrendClass">
            {{ priceChange >= 0 ? '+' : '' }}{{ priceChange }}
          </div>
        </div>
      </div>
    </div>

    <!-- 订单簿内容 -->
    <div class="order-book-content">
      <!-- 表头 -->
      <div class="grid grid-cols-3 gap-2 text-xs text-text-muted mb-2 px-2">
        <span>价格</span>
        <span class="text-right">数量</span>
        <span class="text-right">总计</span>
      </div>

      <!-- 卖单 (红色) -->
      <div class="mb-4">
        <div
          v-for="(order, index) in reversedAsks"
          :key="'ask-' + index"
          class="grid grid-cols-3 gap-2 text-sm py-1 px-2 rounded relative overflow-hidden"
          @click="handleOrderClick(order, 'ask')"
        >
          <!-- 深度条 -->
          <div
            class="absolute top-0 left-0 h-full bg-trading-down/10"
            :style="{ width: `${calculateWidth(order.amount, 'ask')}%` }"
          />

          <span class="text-down font-mono relative z-10">{{ order.price }}</span>
          <span class="text-right font-mono relative z-10">{{ formatNumber(order.amount) }}</span>
          <span class="text-right font-mono text-text-muted relative z-10">
            {{ formatNumber(order.total) }}
          </span>
        </div>
      </div>

      <!-- 分隔线 -->
      <div class="h-px bg-gray-200 dark:bg-gray-700 my-2"></div>

      <!-- 买单 (绿色) -->
      <div>
        <div
          v-for="(order, index) in bids"
          :key="'bid-' + index"
          class="grid grid-cols-3 gap-2 text-sm py-1 px-2 rounded relative overflow-hidden"
          @click="handleOrderClick(order, 'bid')"
        >
          <!-- 深度条 -->
          <div
            class="absolute top-0 left-0 h-full bg-trading-up/10"
            :style="{ width: `${calculateWidth(order.amount, 'bid')}%` }"
          />

          <span class="text-up font-mono relative z-10">{{ order.price }}</span>
          <span class="text-right font-mono relative z-10">{{ formatNumber(order.amount) }}</span>
          <span class="text-right font-mono text-text-muted relative z-10">
            {{ formatNumber(order.total) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-background/50 rounded-xl">
      <div class="spinner"></div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && bids.length === 0 && asks.length === 0" class="text-center py-8 text-text-muted">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
      </svg>
      <p>暂无订单数据</p>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

interface Order {
  price: number
  amount: number
  total: number
}

interface Props {
  title?: string
  bids: Order[]
  asks: Order[]
  currentPrice?: number
  priceChange?: number
  loading?: boolean
  showHeader?: boolean
  showCurrentPrice?: boolean
  maxRows?: number
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  title: '订单簿',
  currentPrice: 0,
  priceChange: 0,
  loading: false,
  showHeader: true,
  showCurrentPrice: true,
  maxRows: 8,
  padding: 'md',
})

const emit = defineEmits<{
  refresh: []
  orderClick: [order: Order, type: 'bid' | 'ask']
}>()

// 反转卖单数组 (从高到低显示)
const reversedAsks = computed(() => {
  return [...props.asks].reverse().slice(0, props.maxRows)
})

// 价格趋势
const priceTrendClass = computed(() => {
  if (props.priceChange > 0) return 'text-up'
  if (props.priceChange < 0) return 'text-down'
  return 'text-neutral'
})

// 计算深度条宽度
const calculateWidth = (amount: number, type: 'bid' | 'ask') => {
  const orders = type === 'bid' ? props.bids : props.asks
  if (orders.length === 0) return 0

  const maxAmount = Math.max(...orders.map(o => o.amount))
  return (amount / maxAmount) * 100
}

// 格式化数字
const formatNumber = (num: number) => {
  return num.toFixed(2)
}

// 处理订单点击
const handleOrderClick = (order: Order, type: 'bid' | 'ask') => {
  emit('orderClick', order, type)
}

// 处理刷新
const handleRefresh = () => {
  emit('refresh')
}
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.order-book {
  position: relative;
  min-height: 300px;
}

/* 当前价格卡片 */
.current-price {
  background: linear-gradient(135deg,
    rgba(59, 130, 246, 0.15) 0%,
    rgba(59, 130, 246, 0.05) 100%
  );
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  transition: all var(--transition-base) var(--ease-default);
}

.current-price:hover {
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
}

/* 订单簿内容 */
.order-book-content {
  position: relative;
}

/* 网格布局 */
.grid {
  display: grid;
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.gap-2 {
  gap: var(--spacing-sm);
}

/* 订单行 */
.order-book-content > div > div {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  cursor: pointer;
  transition: all var(--transition-fast) var(--ease-default);
}

.order-book-content > div > div:hover {
  background: rgba(51, 65, 85, 0.5);
  transform: translateX(2px);
}

/* 深度条 */
.order-book-content > div > div > div:first-child {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  transition: width var(--transition-base) var(--ease-default);
}

/* 文本颜色 */
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

/* 等宽字体 */
.font-mono {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

/* 分隔线 */
.h-px {
  height: 1px;
}

.bg-gray-200 {
  background-color: var(--color-border);
}

.dark\:bg-gray-7 {
  background-color: var(--color-border);
}

.my-2 {
  margin-top: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
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

/* 加载遮罩 */
.absolute {
  position: absolute;
}

.inset-0 {
  inset: 0;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.bg-white\/50 {
  background: rgba(255, 255, 255, 0.5);
}

.dark\:bg-background\/50 {
  background: rgba(15, 23, 42, 0.5);
}

.rounded-xl {
  border-radius: var(--radius-xl);
}

/* 空状态 */
.text-center {
  text-align: center;
}

.py-8 {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-xl);
}

.opacity-50 {
  opacity: 0.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-cols-3 {
    gap: var(--spacing-xs);
    font-size: var(--text-xs);
  }

  .current-price {
    padding: var(--spacing-sm);
  }
}

/* 改进的可点击性 */
.order-book-content > div > div {
  cursor: pointer;
  user-select: none;
}

.order-book-content > div > div:active {
  transform: scale(0.98);
}
</style>
