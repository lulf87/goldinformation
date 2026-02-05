# 交易组件使用指南

本文档详细介绍如何使用黄金交易项目的所有交易相关组件。

---

## 📦 交易组件清单

| 组件 | 文件 | 说明 |
|------|------|------|
| **OrderBook** | `OrderBook.vue` | 订单簿组件 |
| **MarketDepth** | `MarketDepth.vue` | 市场深度组件 |
| **TradingForm** | `TradingForm.vue` | 交易表单组件 |
| **RealtimePriceTicker** | `RealtimePriceTicker.vue` | 实时价格跑马灯 |
| **TradingDashboard** | `TradingDashboard.vue` | 完整交易页面示例 |

---

## 1. OrderBook - 订单簿组件

显示买卖盘的深度信息，支持点击价格填充到交易表单。

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import { OrderBook } from '@/components/trading'

const orderBookData = ref({
  bids: [
    { price: 568.30, amount: 125.5, total: 125.5 },
    { price: 568.25, amount: 89.2, total: 214.7 },
  ],
  asks: [
    { price: 568.55, amount: 145.6, total: 145.6 },
    { price: 568.60, amount: 167.3, total: 312.9 },
  ],
})

const handleRefresh = () => {
  console.log('刷新订单簿')
}

const handleOrderClick = (order, type) => {
  console.log('点击订单:', order, type)
}
</script>

<template>
  <OrderBook
    title="订单簿"
    :bids="orderBookData.bids"
    :asks="orderBookData.asks"
    :current-price="568.50"
    :price-change="2.35"
    :loading="false"
    :max-rows="8"
    @refresh="handleRefresh"
    @order-click="handleOrderClick"
  />
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | `'订单簿'` | 标题 |
| `bids` | `Order[]` | **必填** | 买单数据 |
| `asks` | `Order[]` | **必填** | 卖单数据 |
| `currentPrice` | `number` | `0` | 当前价格 |
| `priceChange` | `number` | `0` | 价格变化 |
| `loading` | `boolean` | `false` | 加载状态 |
| `showHeader` | `boolean` | `true` | 显示头部 |
| `showCurrentPrice` | `boolean` | `true` | 显示当前价格 |
| `maxRows` | `number` | `8` | 最大显示行数 |
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |

### 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `refresh` | - | 刷新订单簿 |
| `orderClick` | `(order: Order, type: 'bid' \| 'ask')` | 点击订单 |

### 数据格式

```typescript
interface Order {
  price: number      // 价格
  amount: number     // 数量
  total: number      // 累计数量
}
```

---

## 2. MarketDepth - 市场深度组件

可视化显示买卖盘深度，支持 Canvas 渲染。

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import { MarketDepth } from '@/components/trading'

const marketDepthData = ref([
  { price: 568.30, bidVolume: 125.5, askVolume: 145.6 },
  { price: 568.40, bidVolume: 89.2, askVolume: 167.3 },
  { price: 568.50, bidVolume: 156.8, askVolume: 198.7 },
])

const handleDepthChange = (level) => {
  console.log('深度变化:', level)
}
</script>

<template>
  <MarketDepth
    title="市场深度"
    :data="marketDepthData"
    :current-price="568.50"
    :loading="false"
    :show-stats="true"
    @depth-change="handleDepthChange"
  />
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | `'市场深度'` | 标题 |
| `data` | `DepthData[]` | **必填** | 深度数据 |
| `currentPrice` | `number` | `0` | 当前价格 |
| `loading` | `boolean` | `false` | 加载状态 |
| `showHeader` | `boolean` | `true` | 显示头部 |
| `showStats` | `boolean` | `true` | 显示统计 |
| `showCurrentPriceLine` | `boolean` | `true` | 显示价格线 |
| `maxDepth` | `number` | `20` | 最大深度 |
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |

### 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `depthChange` | `level: number` | 深度级别变化 |

### 数据格式

```typescript
interface DepthData {
  price: number       // 价格
  bidVolume: number   // 买量
  askVolume: number   // 卖量
}
```

---

## 3. TradingForm - 交易表单组件

完整的交易下单表单，支持买入/卖出、市价单/限价单。

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import { TradingForm } from '@/components/trading'

const orderType = ref('buy')

const handleSubmit = (formData) => {
  console.log('提交订单:', formData)
}

const handleTypeChange = (type) => {
  orderType.value = type
}
</script>

<template>
  <TradingForm
    title="交易下单"
    :order-type="orderType"
    :current-price="568.50"
    :price-change="2.35"
    :available-balance="100000"
    :available-position="100"
    :fee-rate="0.1"
    :loading="false"
    @submit="handleSubmit"
    @type-change="handleTypeChange"
  />
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | `'交易下单'` | 标题 |
| `orderType` | `'buy' \| 'sell'` | `'buy'` | 订单类型 |
| `currentPrice` | `number` | `568.50` | 当前价格 |
| `priceChange` | `number` | `0` | 价格变化 |
| `availableBalance` | `number` | `100000` | 可用余额 |
| `availablePosition` | `number` | `100` | 可用持仓 |
| `feeRate` | `number` | `0.1` | 手续费率(%) |
| `loading` | `boolean` | `false` | 提交中 |
| `showCurrentPrice` | `boolean` | `true` | 显示当前价格 |
| `showQuickAmount` | `boolean` | `true` | 显示快捷数量 |
| `showFee` | `boolean` | `true` | 显示手续费 |
| `showRiskWarning` | `boolean` | `true` | 显示风险提示 |
| `editSymbol` | `boolean` | `true` | 可编辑品种 |
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |

### 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `submit` | `formData: TradingFormData` | 提交订单 |
| `typeChange` | `type: 'buy' \| 'sell'` | 类型变化 |
| `selectSymbol` | - | 选择品种 |

### 暴露的方法

```vue
<script setup>
import { ref } from 'vue'
import { TradingForm } from '@/components/trading'

const tradingFormRef = ref()

const resetForm = () => {
  tradingFormRef.value?.resetForm()
}

const setAmount = (amount) => {
  tradingFormRef.value?.setAmount(10)
}

const setPrice = (price) => {
  tradingFormRef.value?.setPrice(570.00)
}
</script>

<template>
  <TradingForm ref="tradingFormRef" />
</template>
```

---

## 4. RealtimePriceTicker - 实时价格跑马灯

横向滚动的实时价格展示组件。

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import { RealtimePriceTicker } from '@/components/trading'

const tickerItems = ref([
  { symbol: 'AU9999', price: 568.50, changePercent: 0.42, currency: '¥' },
  { symbol: 'XAU/USD', price: 2034.50, changePercent: -0.26, currency: '$' },
  { symbol: 'AG9999', price: 7.28, changePercent: 1.68, currency: '¥' },
])

const handleItemClick = (item) => {
  console.log('点击:', item)
}
</script>

<template>
  <RealtimePriceTicker
    :items="tickerItems"
    label="实时行情"
    pause-on-hover
    @item-click="handleItemClick"
  />
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `items` | `PriceItem[]` | **必填** | 价格数据 |
| `label` | `string` | `'实时行情'` | 标签 |
| `variant` | `'horizontal' \| 'vertical'` | `'horizontal'` | 方向 |
| `showLabel` | `boolean` | `true` | 显示标签 |
| `showTime` | `boolean` | `false` | 显示时间 |
| `showDivider` | `boolean` | `true` | 显示分隔线 |
| `pauseOnHover` | `boolean` | `true` | 悬停暂停 |
| `speed` | `'slow' \| 'normal' \| 'fast'` | `'normal'` | 滚动速度 |
| `itemGap` | `string` | `'2rem'` | 项目间距 |

### 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `itemClick` | `item: PriceItem` | 点击项目 |

---

## 5. TradingDashboard - 完整交易页面

包含所有组件的完整交易页面示例。

### 使用方式

```typescript
// router/index.ts
{
  path: '/trading',
  component: () => import('@/views/TradingDashboard.vue')
}
```

---

## 🎯 完整集成示例

### 在您的页面中使用所有交易组件

```vue
<script setup>
import { ref } from 'vue'
import {
  OrderBook,
  MarketDepth,
  TradingForm,
  RealtimePriceTicker,
} from '@/components/trading'
import { BaseCard, BaseModal, BaseButton } from '@/components/ui'

// 数据
const currentPrice = ref(568.50)
const orderType = ref('buy')
const showModal = ref(false)

// 跑马灯数据
const tickerItems = ref([
  { symbol: 'AU9999', price: 568.50, changePercent: 0.42, currency: '¥' },
  { symbol: 'XAU/USD', price: 2034.50, changePercent: -0.26, currency: '$' },
])

// 订单簿数据
const orderBookData = ref({
  bids: [
    { price: 568.30, amount: 125.5, total: 125.5 },
    { price: 568.25, amount: 89.2, total: 214.7 },
  ],
  asks: [
    { price: 568.55, amount: 145.6, total: 145.6 },
    { price: 568.60, amount: 167.3, total: 312.9 },
  ],
})

// 市场深度数据
const marketDepthData = ref([
  { price: 568.30, bidVolume: 125.5, askVolume: 145.6 },
  { price: 568.40, bidVolume: 89.2, askVolume: 167.3 },
])

// 处理订单点击
const handleOrderClick = (order, type) => {
  console.log('点击订单:', order, type)
  // 填充到交易表单
}
</script>

<template>
  <div class="min-h-screen bg-background p-4">
    <!-- 跑马灯 -->
    <RealtimePriceTicker
      :items="tickerItems"
      class="mb-6"
    />

    <!-- 主内容 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧: 交易表单 -->
      <div class="space-y-6">
        <TradingForm
          :order-type="orderType"
          :current-price="currentPrice"
          @submit="console.log($event)"
          @type-change="orderType = $event"
        />
      </div>

      <!-- 中间: 订单簿 -->
      <div>
        <OrderBook
          :bids="orderBookData.bids"
          :asks="orderBookData.asks"
          :current-price="currentPrice"
          @order-click="handleOrderClick"
        />
      </div>

      <!-- 右侧: 市场深度 -->
      <div>
        <MarketDepth
          :data="marketDepthData"
          :current-price="currentPrice"
        />
      </div>
    </div>
  </div>
</template>
```

---

## 🔧 实际应用场景

### 场景 1: 点击订单簿价格自动填充

```vue
<script setup>
import { ref } from 'vue'
import { OrderBook, TradingForm } from '@/components/trading'

const tradingFormRef = ref()

const handleOrderClick = (order, type) => {
  // 自动填充价格到交易表单
  tradingFormRef.value?.setPrice(order.price)

  // 自动切换到对应类型
  if (type === 'bid') {
    tradingFormRef.value?.setOrderType('buy')
  } else {
    tradingFormRef.value?.setOrderType('sell')
  }
}
</script>

<template>
  <OrderBook @order-click="handleOrderClick" />
  <TradingForm ref="tradingFormRef" />
</template>
```

### 场景 2: 实时更新价格

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RealtimePriceTicker } from '@/components/trading'

const tickerItems = ref([])

let intervalId = null

const fetchPrices = async () => {
  const response = await fetch('/api/prices')
  tickerItems.value = await response.json()
}

onMounted(() => {
  fetchPrices()
  intervalId = setInterval(fetchPrices, 3000) // 每3秒更新
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<template>
  <RealtimePriceTicker :items="tickerItems" />
</template>
```

### 场景 3: 提交订单

```vue
<script setup>
import { ref } from 'vue'
import { TradingForm } from '@/components/trading'
import { BaseModal } from '@/components/ui'

const showSuccessModal = ref(false)
const lastOrder = ref(null)

const handleSubmit = async (formData) => {
  try {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })

    const result = await response.json()
    lastOrder.value = result
    showSuccessModal.value = true
  } catch (error) {
    console.error('提交失败:', error)
  }
}
</script>

<template>
  <TradingForm
    :loading="isSubmitting"
    @submit="handleSubmit"
  />

  <BaseModal v-model="showSuccessModal" title="交易成功">
    <p>订单号: {{ lastOrder?.id }}</p>
  </BaseModal>
</template>
```

---

## 📊 数据格式参考

### OrderBook 数据格式

```typescript
interface Order {
  price: number      // 价格，如 568.50
  amount: number     // 数量，如 125.5
  total: number      // 累计数量，从第一条到当前条的累计
}
```

### MarketDepth 数据格式

```typescript
interface DepthData {
  price: number       // 价格档位
  bidVolume: number   // 买量
  askVolume: number   // 卖量
}
```

### TradingForm 提交数据格式

```typescript
interface TradingFormData {
  symbol: string               // 交易品种，如 "AU9999"
  orderType: 'market' | 'limit' // 订单类型
  leverage: number             // 杠杆倍数，如 10
  limitPrice?: number          // 限价单价格
  amount: number               // 数量
}
```

---

## 💡 最佳实践

### 1. 数据刷新

```vue
<script setup>
import { ref } from 'vue'

const orderBookData = ref({ bids: [], asks: [] })
const isLoading = ref(false)

const refreshData = async () => {
  isLoading.value = true
  try {
    const response = await fetch('/api/orderbook')
    orderBookData.value = await response.json()
  } finally {
    isLoading.value = false
  }
}

// 定时刷新
onMounted(() => {
  refreshData()
  const interval = setInterval(refreshData, 5000)
  onUnmounted(() => clearInterval(interval))
})
</script>
```

### 2. WebSocket 实时推送

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const tickerItems = ref([])
let ws = null

onMounted(() => {
  ws = new WebSocket('wss://api.example.com/ws/prices')

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    tickerItems.value = data.prices
  }
})

onUnmounted(() => {
  ws?.close()
})
</script>
```

### 3. 错误处理

```vue
<script setup>
import { ref } from 'vue'

const error = ref(null)

const handleSubmit = async (formData) => {
  error.value = null

  try {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      throw new Error('提交失败')
    }

    const result = await response.json()
    console.log('成功:', result)
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <TradingForm @submit="handleSubmit" />
  <div v-if="error" class="text-down mt-2">
    {{ error }}
  </div>
</template>
```

---

## 🎯 完整示例

查看 `TradingDashboard.vue` 获取完整的使用示例。

---

## 📚 相关文档

- **UI 组件指南**: `UI_COMPONENTS_GUIDE.md`
- **设计系统**: `design-system/gold-trading/MASTER.md`
- **TypeScript 类型**: `frontend/src/components/trading/types.ts`

---

**立即开始构建您的交易应用！** 🚀
