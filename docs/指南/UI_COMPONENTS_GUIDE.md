# UI 组件使用指南

本文档展示了如何使用基于设计系统创建的可复用 Vue 组件。

---

## 📦 已创建的组件

1. **BaseButton** - 按钮组件
2. **BaseCard** - 卡片组件
3. **BaseModal** - 模态框组件
4. **BaseInput** - 输入框组件
5. **TradingPriceCard** - 交易价格卡片组件

---

## 1. BaseButton - 按钮组件

### 基础用法

```vue
<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'

const handleClick = () => {
  console.log('按钮被点击')
}
</script>

<template>
  <!-- 主按钮 -->
  <BaseButton @click="handleClick">主要操作</BaseButton>

  <!-- 次要按钮 -->
  <BaseButton variant="secondary">次要操作</BaseButton>

  <!-- CTA 按钮 (橙色) -->
  <BaseButton variant="cta">立即开始</BaseButton>

  <!-- 幽灵按钮 -->
  <BaseButton variant="ghost">取消</BaseButton>

  <!-- 危险按钮 -->
  <BaseButton variant="danger">删除</BaseButton>
</template>
```

### 不同尺寸

```vue
<template>
  <BaseButton size="sm">小按钮</BaseButton>
  <BaseButton size="md">中按钮</BaseButton>
  <BaseButton size="lg">大按钮</BaseButton>
</template>
```

### 状态变体

```vue
<script setup>
import { ref } from 'vue'

const loading = ref(false)
const disabled = ref(false)

const handleSubmit = async () => {
  loading.value = true
  // 模拟异步操作
  await new Promise(resolve => setTimeout(resolve, 2000))
  loading.value = false
}
</script>

<template>
  <!-- 加载中 -->
  <BaseButton :loading="loading" @click="handleSubmit">
    提交
  </BaseButton>

  <!-- 禁用 -->
  <BaseButton :disabled="true">禁用按钮</BaseButton>

  <!-- 块级按钮 (全宽) -->
  <BaseButton block>全宽按钮</BaseButton>
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `'primary' \| 'secondary' \| 'cta' \| 'ghost' \| 'danger'` | `'primary'` | 按钮变体 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 按钮尺寸 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `loading` | `boolean` | `false` | 是否加载中 |
| `block` | `boolean` | `false` | 是否全宽 |
| `nativeType` | `'button' \| 'submit' \| 'reset'` | `'button'` | 原生按钮类型 |

---

## 2. BaseCard - 卡片组件

### 基础用法

```vue
<script setup>
import BaseCard from '@/components/ui/BaseCard.vue'

const handleCardClick = () => {
  console.log('卡片被点击')
}
</script>

<template>
  <!-- 默认卡片 -->
  <BaseCard>
    <h3>卡片标题</h3>
    <p>卡片内容</p>
  </BaseCard>

  <!-- 可悬停卡片 -->
  <BaseCard hoverable @click="handleCardClick">
    <h3>点击我</h3>
  </BaseCard>

  <!-- 玻璃态卡片 -->
  <BaseCard variant="glass">
    <h3>毛玻璃效果</h3>
  </BaseCard>

  <!-- 带边框卡片 -->
  <BaseCard variant="bordered">
    <h3>带边框</h3>
  </BaseCard>
</template>
```

### 自定义内边距

```vue
<template>
  <BaseCard padding="sm">小内边距</BaseCard>
  <BaseCard padding="md">中等内边距</BaseCard>
  <BaseCard padding="lg">大内边距</BaseCard>
  <BaseCard padding="none">无内边距</BaseCard>
</template>
```

### 自定义阴影

```vue
<template>
  <BaseCard shadow="sm">小阴影</BaseCard>
  <BaseCard shadow="md">中等阴影</BaseCard>
  <BaseCard shadow="lg">大阴影</BaseCard>
  <BaseCard shadow="xl">超大阴影</BaseCard>
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `'default' \| 'glass' \| 'bordered'` | `'default'` | 卡片变体 |
| `hoverable` | `boolean` | `false` | 是否可悬停 |
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |
| `shadow` | `'none' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | 阴影 |

---

## 3. BaseModal - 模态框组件

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const showModal = ref(false)
const handleConfirm = () => {
  console.log('确认')
  showModal.value = false
}
</script>

<template>
  <!-- 触发按钮 -->
  <BaseButton @click="showModal = true">打开模态框</BaseButton>

  <!-- 模态框 -->
  <BaseModal
    v-model="showModal"
    title="确认操作"
    @confirm="handleConfirm"
  >
    <p>您确定要执行此操作吗？</p>

    <template #footer>
      <BaseButton variant="ghost" @click="showModal = false">
        取消
      </BaseButton>
      <BaseButton variant="danger" @click="handleConfirm">
        确认删除
      </BaseButton>
    </template>
  </BaseModal>
</template>
```

### 自定义头部

```vue
<template>
  <BaseModal v-model="showModal">
    <template #header>
      <div class="flex items-center gap-2">
        <svg class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h2 class="text-xl font-bold">自定义标题</h2>
      </div>
    </template>

    <p>模态框内容</p>
  </BaseModal>
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `modelValue` | `boolean` | **必填** | 是否显示模态框 |
| `title` | `string` | - | 标题 |
| `closable` | `boolean` | `true` | 是否显示关闭按钮 |
| `closeOnOverlay` | `boolean` | `true` | 点击遮罩是否关闭 |

---

## 4. BaseInput - 输入框组件

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const text = ref('')
const email = ref('')
const password = ref('')
const number = ref(0)
</script>

<template>
  <!-- 文本输入 -->
  <BaseInput
    v-model="text"
    label="用户名"
    placeholder="请输入用户名"
  />

  <!-- 邮箱输入 -->
  <BaseInput
    v-model="email"
    type="email"
    label="邮箱地址"
    placeholder="example@mail.com"
  />

  <!-- 密码输入 -->
  <BaseInput
    v-model="password"
    type="password"
    label="密码"
    placeholder="请输入密码"
  />

  <!-- 数字输入 -->
  <BaseInput
    v-model.number="number"
    type="number"
    label="金额"
    :min="0"
    :max="1000000"
    :step="100"
  />
</template>
```

### 带验证的输入框

```vue
<script setup>
import { ref, computed } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const username = ref('')
const error = computed(() => {
  if (username.value.length < 3) {
    return '用户名至少需要3个字符'
  }
  return ''
})
</script>

<template>
  <BaseInput
    v-model="username"
    label="用户名"
    :error="error"
    helpText="3-20个字符"
    required
  />
</template>
```

### 带图标的输入框

```vue
<template>
  <!-- 前缀图标 -->
  <BaseInput
    v-model="search"
    placeholder="搜索..."
  >
    <template #prefix>
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </template>
  </BaseInput>

  <!-- 可清除的输入框 -->
  <BaseInput
    v-model="text"
    label="可输入"
    clearable
  />

  <!-- 后缀图标 -->
  <BaseInput
    v-model="amount"
    type="number"
    label="金额"
  >
    <template #suffix>
      <span class="text-text-muted">¥</span>
    </template>
  </BaseInput>
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `modelValue` | `string \| number` | **必填** | 输入值 |
| `type` | `'text' \| 'password' \| 'email' \| 'number' \| 'tel'` | `'text'` | 输入类型 |
| `label` | `string` | - | 标签 |
| `placeholder` | `string` | - | 占位符 |
| `helpText` | `string` | - | 帮助文本 |
| `error` | `string` | - | 错误提示 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `readonly` | `boolean` | `false` | 是否只读 |
| `required` | `boolean` | `false` | 是否必填 |
| `clearable` | `boolean` | `false` | 是否可清除 |
| `maxlength` | `number` | - | 最大长度 |
| `min` | `number` | - | 最小值 |
| `max` | `number` | - | 最大值 |
| `step` | `number` | - | 步长 |

### 暴露的方法

```vue
<script setup>
import { ref } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const inputRef = ref()

const focusInput = () => {
  inputRef.value?.focus()
}

const blurInput = () => {
  inputRef.value?.blur()
}
</script>

<template>
  <BaseInput
    ref="inputRef"
    v-model="text"
    label="自动聚焦"
  />

  <BaseButton @click="focusInput">聚焦</BaseButton>
  <BaseButton @click="blurInput">失焦</BaseButton>
</template>
```

---

## 5. TradingPriceCard - 交易价格卡片

### 基础用法

```vue
<script setup>
import { ref } from 'vue'
import TradingPriceCard from '@/components/ui/TradingPriceCard.vue'

const goldPrice = ref({
  title: '黄金现货',
  symbol: 'AU9999',
  price: 568.50,
  currency: '¥',
  change: 2.35,
  changePercent: 0.42,
})
</script>

<template>
  <TradingPriceCard
    :title="goldPrice.title"
    :symbol="goldPrice.symbol"
    :price="goldPrice.price"
    :currency="goldPrice.currency"
    :change="goldPrice.change"
    :changePercent="goldPrice.changePercent"
  />
</template>
```

### 完整示例（带数据列表）

```vue
<script setup>
import { ref } from 'vue'
import TradingPriceCard from '@/components/ui/TradingPriceCard.vue'

const goldData = ref({
  title: '黄金现货',
  symbol: 'AU9999',
  price: 568.50,
  currency: '¥',
  change: 2.35,
  changePercent: 0.42,
  dataList: [
    { label: '今开', value: '566.80' },
    { label: '最高', value: '569.20' },
    { label: '最低', value: '565.30' },
    { label: '昨收', value: '566.15' },
  ],
  progress: 75, // 75% 的买盘
})
</script>

<template>
  <TradingPriceCard
    :title="goldData.title"
    :symbol="goldData.symbol"
    :price="goldData.price"
    :currency="goldData.currency"
    :change="goldData.change"
    :changePercent="goldData.changePercent"
    :data-list="goldData.dataList"
    :progress="goldData.progress"
    show-progress
    hoverable
    @click="handleCardClick"
  >
    <template #footer>
      <BaseButton size="sm" variant="primary">
        查看详情
      </BaseButton>
    </template>
  </TradingPriceCard>
</template>
```

### 加载状态

```vue
<template>
  <TradingPriceCard
    title="黄金现货"
    :price="0"
    :loading="true"
  />
</template>
```

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | **必填** | 标题 |
| `symbol` | `string` | - | 交易代码 |
| `price` | `number` | **必填** | 当前价格 |
| `currency` | `string` | `'¥'` | 货币符号 |
| `change` | `number \| null` | `null` | 涨跌额 |
| `changePercent` | `number \| null` | `null` | 涨跌幅(%) |
| `dataList` | `DataItem[]` | `[]` | 数据列表 |
| `showHeader` | `boolean` | `true` | 是否显示头部 |
| `showTrendIcon` | `boolean` | `true` | 是否显示趋势图标 |
| `showProgress` | `boolean` | `false` | 是否显示进度条 |
| `progress` | `number \| null` | `null` | 进度(0-100) |
| `loading` | `boolean` | `false` | 是否加载中 |
| `hoverable` | `boolean` | `false` | 是否可点击 |
| `variant` | `'default' \| 'glass' \| 'bordered'` | `'default'` | 卡片变体 |
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | 内边距 |
| `shadow` | `'none' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | 阴影 |

### 插槽

| 插槽名 | 说明 |
|--------|------|
| `footer` | 底部内容 |

---

## 🎨 完整示例: 交易仪表板

```vue
<script setup>
import { ref, onMounted } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import TradingPriceCard from '@/components/ui/TradingPriceCard.vue'

const showModal = ref(false)
const searchQuery = ref('')

const prices = ref([
  {
    title: '黄金现货',
    symbol: 'AU9999',
    price: 568.50,
    change: 2.35,
    changePercent: 0.42,
    dataList: [
      { label: '今开', value: '566.80' },
      { label: '最高', value: '569.20' },
      { label: '最低', value: '565.30' },
    ],
  },
  {
    title: '国际金价',
    symbol: 'XAU/USD',
    price: 2034.50,
    currency: '$',
    change: -5.30,
    changePercent: -0.26,
    dataList: [
      { label: '今开', value: '2038.00' },
      { label: '最高', value: '2041.20' },
      { label: '最低', value: '2032.10' },
    ],
  },
])

const refreshPrices = async () => {
  // 模拟刷新
  console.log('刷新价格...')
}
</script>

<template>
  <div class="min-h-screen bg-background p-8">
    <!-- 头部 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-4">黄金交易市场</h1>

      <!-- 搜索栏 -->
      <div class="flex gap-4">
        <BaseInput
          v-model="searchQuery"
          placeholder="搜索交易品种..."
          class="flex-1"
        >
          <template #prefix>
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </template>
        </BaseInput>

        <BaseButton variant="cta" @click="refreshPrices">
          刷新数据
        </BaseButton>
      </div>
    </div>

    <!-- 价格卡片网格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <TradingPriceCard
        v-for="(item, index) in prices"
        :key="index"
        :title="item.title"
        :symbol="item.symbol"
        :price="item.price"
        :change="item.change"
        :changePercent="item.changePercent"
        :data-list="item.dataList"
        hoverable
      />
    </div>

    <!-- 模态框示例 -->
    <BaseModal v-model="showModal" title="交易确认">
      <p>您确定要执行此交易吗？</p>

      <template #footer>
        <BaseButton variant="ghost" @click="showModal = false">
          取消
        </BaseButton>
        <BaseButton variant="primary" @click="showModal = false">
          确认
        </BaseButton>
      </template>
    </BaseModal>
  </div>
</template>
```

---

## 🎯 最佳实践

### 1. 使用 TypeScript 类型

```typescript
// 推荐定义接口
interface PriceData {
  title: string
  symbol: string
  price: number
  change: number
  changePercent: number
}

const prices = ref<PriceData[]>([])
```

### 2. 组合多个组件

```vue
<template>
  <BaseCard>
    <BaseInput v-model="username" label="用户名" />
    <BaseInput v-model="password" type="password" label="密码" class="mt-4" />
    <BaseButton class="mt-6" block @click="login">登录</BaseButton>
  </BaseCard>
</template>
```

### 3. 响应式布局

```vue
<template>
  <!-- 移动端单列，平板双列，桌面三列 -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <TradingPriceCard v-for="item in items" :key="item.id" v-bind="item" />
  </div>
</template>
```

### 4. 加载和错误状态

```vue
<script setup>
import { ref } from 'vue'

const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  try {
    await someAsyncOperation()
  } catch (err) {
    error.value = '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseCard>
    <BaseInput
      v-model="username"
      label="用户名"
      :error="error"
    />
    <BaseButton
      :loading="loading"
      @click="handleSubmit"
      class="mt-4"
    >
      提交
    </BaseButton>
  </BaseCard>
</template>
```

---

## 📝 总结

所有组件都:
- ✅ 基于 Design System 构建
- ✅ 支持暗色模式
- ✅ 支持无障碍访问
- ✅ TypeScript 类型支持
- ✅ 响应式设计
- ✅ 可组合使用

立即在您的项目中使用这些组件，加快开发速度！
