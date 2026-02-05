<template>
  <div class="min-h-screen bg-background dark:bg-background text-text dark:text-text p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <header class="mb-8">
        <h1 class="text-3xl font-bold mb-2">UI 组件库 - 快速开始</h1>
        <p class="text-text-muted">
          基于设计系统的可复用 Vue 3 组件展示
        </p>
      </header>

      <!-- 按钮展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">按钮组件</h2>
        <BaseCard>
          <div class="space-y-4">
            <!-- 不同变体 -->
            <div>
              <h3 class="text-sm font-medium text-text-muted mb-2">按钮变体</h3>
              <div class="flex flex-wrap gap-3">
                <BaseButton variant="primary">主要按钮</BaseButton>
                <BaseButton variant="secondary">次要按钮</BaseButton>
                <BaseButton variant="cta">CTA 按钮</BaseButton>
                <BaseButton variant="ghost">幽灵按钮</BaseButton>
                <BaseButton variant="danger">危险按钮</BaseButton>
              </div>
            </div>

            <!-- 不同尺寸 -->
            <div>
              <h3 class="text-sm font-medium text-text-muted mb-2">按钮尺寸</h3>
              <div class="flex flex-wrap items-center gap-3">
                <BaseButton size="sm">小按钮</BaseButton>
                <BaseButton size="md">中按钮</BaseButton>
                <BaseButton size="lg">大按钮</BaseButton>
              </div>
            </div>

            <!-- 状态变体 -->
            <div>
              <h3 class="text-sm font-medium text-text-muted mb-2">状态变体</h3>
              <div class="flex flex-wrap gap-3">
                <BaseButton :loading="true">加载中</BaseButton>
                <BaseButton :disabled="true">禁用</BaseButton>
                <BaseButton block>块级按钮</BaseButton>
              </div>
            </div>
          </div>
        </BaseCard>
      </section>

      <!-- 卡片展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">卡片组件</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 默认卡片 -->
          <BaseCard>
            <h3 class="text-lg font-semibold mb-2">默认卡片</h3>
            <p class="text-text-muted text-sm">
              这是基础的卡片样式，包含阴影和圆角。
            </p>
          </BaseCard>

          <!-- 玻璃态卡片 -->
          <BaseCard variant="glass">
            <h3 class="text-lg font-semibold mb-2">玻璃态卡片</h3>
            <p class="text-text-muted text-sm">
              带有毛玻璃背景效果的卡片。
            </p>
          </BaseCard>

          <!-- 可悬停卡片 -->
          <BaseCard hoverable @click="handleCardClick">
            <h3 class="text-lg font-semibold mb-2">可悬停卡片</h3>
            <p class="text-text-muted text-sm">
              鼠标悬停时有阴影和位移效果，点击可触发事件。
            </p>
          </BaseCard>
        </div>
      </section>

      <!-- 输入框展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">输入框组件</h2>
        <BaseCard>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 基础输入框 -->
            <BaseInput
              v-model="formData.username"
              label="用户名"
              placeholder="请输入用户名"
            />

            <!-- 邮箱输入框 -->
            <BaseInput
              v-model="formData.email"
              type="email"
              label="邮箱"
              placeholder="example@mail.com"
            />

            <!-- 带验证的输入框 -->
            <BaseInput
              v-model="formData.password"
              type="password"
              label="密码"
              placeholder="请输入密码"
              :error="passwordError"
              help-text="至少8个字符"
              required
            />

            <!-- 可清除的输入框 -->
            <BaseInput
              v-model="formData.search"
              label="搜索"
              placeholder="输入关键词..."
              clearable
            >
              <template #prefix>
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </template>
            </BaseInput>

            <!-- 数字输入框 -->
            <BaseInput
              v-model.number="formData.amount"
              type="number"
              label="金额"
              :min="0"
              :max="1000000"
              :step="100"
            >
              <template #suffix>
                <span class="text-text-muted">¥</span>
              </template>
            </BaseInput>

            <!-- 只读输入框 -->
            <BaseInput
              v-model="formData.readonly"
              label="只读字段"
              readonly
            />
          </div>
        </BaseCard>
      </section>

      <!-- 交易价格卡片展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">交易价格卡片</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- 上涨示例 -->
          <TradingPriceCard
            title="黄金现货"
            symbol="AU9999"
            :price="568.50"
            currency="¥"
            :change="2.35"
            :change-percent="0.42"
            :data-list="[
              { label: '今开', value: '566.80' },
              { label: '最高', value: '569.20' },
              { label: '最低', value: '565.30' },
            ]"
            :progress="75"
            show-progress
            hoverable
          />

          <!-- 下跌示例 -->
          <TradingPriceCard
            title="国际金价"
            symbol="XAU/USD"
            :price="2034.50"
            currency="$"
            :change="-5.30"
            :change-percent="-0.26"
            :data-list="[
              { label: '今开', value: '2038.00' },
              { label: '最高', value: '2041.20' },
              { label: '最低', value: '2032.10' },
            ]"
            :progress="35"
            show-progress
            hoverable
          />

          <!-- 加载状态 -->
          <TradingPriceCard
            title="白银现货"
            symbol="AG9999"
            :price="0"
            :loading="true"
          />
        </div>
      </section>

      <!-- 模态框展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">模态框组件</h2>
        <BaseCard>
          <div class="flex gap-3">
            <BaseButton @click="showModal = true">打开模态框</BaseButton>
            <BaseButton @click="showConfirmModal = true" variant="cta">
              确认对话框
            </BaseButton>
          </div>
        </BaseCard>
      </section>

      <!-- 标签展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">标签组件</h2>
        <BaseCard>
          <div class="flex flex-wrap gap-3">
            <span class="badge badge-success">成功</span>
            <span class="badge badge-warning">警告</span>
            <span class="badge badge-danger">错误</span>
            <span class="badge badge-info">信息</span>
          </div>

          <div class="mt-4 flex flex-wrap gap-3">
            <span class="badge badge-success">上涨 +2.35%</span>
            <span class="badge badge-danger">下跌 -1.20%</span>
            <span class="badge badge-info">中性 0.00%</span>
          </div>
        </BaseCard>
      </section>

      <!-- 文本颜色展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">交易专用颜色</h2>
        <BaseCard>
          <div class="space-y-3">
            <div class="flex items-center gap-4">
              <span class="text-up font-mono text-lg">+2.35%</span>
              <span class="text-text-muted text-sm">上涨 (绿色)</span>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-down font-mono text-lg">-1.20%</span>
              <span class="text-text-muted text-sm">下跌 (红色)</span>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-neutral font-mono text-lg">0.00%</span>
              <span class="text-text-muted text-sm">中性 (灰色)</span>
            </div>
          </div>
        </BaseCard>
      </section>

      <!-- 动画展示 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">动画效果</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- 脉冲动画 -->
          <BaseCard>
            <h3 class="text-sm font-medium text-text-muted mb-3">脉冲动画</h3>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
          </BaseCard>

          <!-- 旋转动画 -->
          <BaseCard>
            <h3 class="text-sm font-medium text-text-muted mb-3">旋转动画</h3>
            <div class="flex justify-center">
              <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          </BaseCard>

          <!-- 闪烁动画 -->
          <BaseCard>
            <h3 class="text-sm font-medium text-text-muted mb-3">闪烁动画</h3>
            <div class="flex justify-center">
              <div class="px-4 py-2 bg-primary text-white rounded animate-blink">
                实时数据
              </div>
            </div>
          </BaseCard>
        </div>
      </section>
    </div>

    <!-- 模态框 -->
    <BaseModal v-model="showModal" title="模态框标题">
      <p class="mb-4">这是一个基础的模态框示例。</p>
      <p class="text-text-muted text-sm">
        模态框支持 ESC 键关闭、点击遮罩关闭等功能。
      </p>

      <template #footer>
        <BaseButton variant="ghost" @click="showModal = false">
          取消
        </BaseButton>
        <BaseButton variant="primary" @click="showModal = false">
          确认
        </BaseButton>
      </template>
    </BaseModal>

    <!-- 确认对话框 -->
    <BaseModal v-model="showConfirmModal" title="确认操作">
      <div class="mb-4">
        <svg class="h-12 w-12 text-cta mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-center">您确定要执行此操作吗？此操作无法撤销。</p>
      </div>

      <template #footer>
        <BaseButton variant="ghost" @click="showConfirmModal = false">
          取消
        </BaseButton>
        <BaseButton variant="danger" @click="showConfirmModal = false">
          确认删除
        </BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import TradingPriceCard from '@/components/ui/TradingPriceCard.vue'

// 表单数据
const formData = ref({
  username: '',
  email: '',
  password: '',
  search: '',
  amount: 0,
  readonly: '这是只读内容',
})

// 密码验证
const passwordError = computed(() => {
  if (formData.value.password.length === 0) return ''
  if (formData.value.password.length < 8) {
    return '密码至少需要8个字符'
  }
  return ''
})

// 模态框状态
const showModal = ref(false)
const showConfirmModal = ref(false)

// 卡片点击处理
const handleCardClick = () => {
  console.log('卡片被点击')
  // 可以添加路由跳转或其他逻辑
}
</script>

<style scoped>
/* 添加额外的自定义样式 */
section {
  scroll-margin-top: 2rem;
}

/* 响应式网格 */
@media (max-width: 768px) {
  section {
    margin-bottom: 2rem;
  }
}
</style>
