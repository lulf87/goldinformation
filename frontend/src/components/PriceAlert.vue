<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-[#F8FAFC] flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        价格预警
      </h2>
      <button
        @click="showCreateForm = !showCreateForm"
        class="text-sm px-3 py-1.5 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-100 transition-colors flex items-center gap-1"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ showCreateForm ? '取消' : '添加预警' }}
      </button>
    </div>

    <!-- Create Alert Form -->
    <div
      v-if="showCreateForm"
      class="mb-4 p-4 bg-slate-700/30 rounded-lg border border-slate-600/30 fade-in-up"
    >
      <form @submit.prevent="createAlert" class="space-y-3">
        <div>
          <label class="block text-sm text-slate-400 mb-1.5">预警价格</label>
          <input
            v-model.number="newAlertPrice"
            type="number"
            step="0.01"
            placeholder="输入价格,如 2750.00"
            class="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#F59E0B] focus:ring-1 focus:ring-[#F59E0B]"
            required
          />
        </div>

        <div>
          <label class="block text-sm text-slate-400 mb-1.5">触发条件</label>
          <select
            v-model="newAlertCondition"
            class="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-200 focus:outline-none focus:border-[#F59E0B] focus:ring-1 focus:ring-[#F59E0B]"
          >
            <option value="above">高于</option>
            <option value="below">低于</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-slate-400 mb-1.5">备注 (可选)</label>
          <input
            v-model="newAlertNote"
            type="text"
            placeholder="如: 突破阻力位"
            class="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#F59E0B] focus:ring-1 focus:ring-[#F59E0B]"
          />
        </div>

        <div class="flex gap-2">
          <button
            type="submit"
            class="flex-1 btn btn-primary"
          >
            设置预警
          </button>
          <button
            type="button"
            @click="showCreateForm = false"
            class="px-4 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            取消
          </button>
        </div>
      </form>
    </div>

    <!-- Active Alerts -->
    <div v-if="alerts.length === 0" class="text-center py-8">
      <svg class="w-12 h-12 mx-auto text-slate-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      <p class="text-slate-500 text-sm">暂无预警设置</p>
      <p class="text-slate-600 text-xs mt-1">点击上方按钮添加价格预警</p>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="alert in sortedAlerts"
        :key="alert.id"
        class="relative p-3 rounded-lg border transition-all duration-200"
        :class="getAlertCardClass(alert)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span
                class="text-xs px-2 py-0.5 rounded"
                :class="alert.condition === 'above' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'"
              >
                {{ alert.condition === 'above' ? '高于' : '低于' }}
              </span>
              <span class="text-lg font-bold mono-number" :class="getPriceTextClass(alert)">
                ${{ alert.price.toFixed(2) }}
              </span>
            </div>
            <p v-if="alert.note" class="text-xs text-slate-400 mt-1">{{ alert.note }}</p>
            <p class="text-xs text-slate-500 mt-1">
              创建于 {{ formatDate(alert.createdAt) }}
            </p>
          </div>
          <button
            @click="deleteAlert(alert.id)"
            class="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
            title="删除预警"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <!-- Distance indicator -->
        <div class="mt-2 pt-2 border-t border-slate-700/50">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-500">距离当前价</span>
            <span
              class="font-medium mono-number"
              :class="getDistanceClass(alert)"
            >
              {{ formatDistance(alert) }}
            </span>
          </div>
          <!-- Progress bar -->
          <div class="mt-2 h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-300"
              :class="getProgressClass(alert)"
              :style="{ width: calculateProgress(alert) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

interface Alert {
  id: string
  price: number
  condition: 'above' | 'below'
  note?: string
  createdAt: Date
}

const store = useAnalysisStore()

// Form state
const showCreateForm = ref(false)
const newAlertPrice = ref<number>(2750)
const newAlertCondition = ref<'above' | 'below'>('above')
const newAlertNote = ref('')

// Alert state
const alerts = ref<Alert[]>([
  // Example alert
  {
    id: '1',
    price: 2760,
    condition: 'above',
    note: '突破阻力位',
    createdAt: new Date(Date.now() - 3600000), // 1 hour ago
  },
])

// Computed properties
const sortedAlerts = computed(() => {
  return [...alerts.value].sort((a, b) => {
    const priceA = Math.abs(a.price - (store.analysis?.current_price || 0))
    const priceB = Math.abs(b.price - (store.analysis?.current_price || 0))
    return priceA - priceB
  })
})

// Methods
function createAlert() {
  if (!newAlertPrice.value) return

  const alert: Alert = {
    id: Date.now().toString(),
    price: newAlertPrice.value,
    condition: newAlertCondition.value,
    note: newAlertNote.value || undefined,
    createdAt: new Date(),
  }

  alerts.value.push(alert)

  // Reset form
  newAlertPrice.value = store.analysis?.current_price || 2750
  newAlertCondition.value = 'above'
  newAlertNote.value = ''
  showCreateForm.value = false
}

function deleteAlert(id: string) {
  alerts.value = alerts.value.filter((a) => a.id !== id)
}

function getAlertCardClass(alert: Alert) {
  const currentPrice = store.analysis?.current_price || 0
  const distance = Math.abs(alert.price - currentPrice)
  const isClose = distance < 10

  return [
    'bg-slate-700/20',
    'border-slate-600/30',
    isClose ? 'gradient-border-gold' : '',
    alert.condition === 'above' && currentPrice > alert.price ? 'opacity-50' : '',
    alert.condition === 'below' && currentPrice < alert.price ? 'opacity-50' : '',
  ].join(' ')
}

function getPriceTextClass(alert: Alert) {
  const currentPrice = store.analysis?.current_price || 0
  if (alert.condition === 'above' && currentPrice > alert.price) return 'text-slate-500 line-through'
  if (alert.condition === 'below' && currentPrice < alert.price) return 'text-slate-500 line-through'
  return 'text-[#F59E0B]'
}

function getDistanceClass(alert: Alert) {
  const currentPrice = store.analysis?.current_price || 0
  const distance = Math.abs(alert.price - currentPrice)
  if (distance < 5) return 'text-emerald-400'
  if (distance < 15) return 'text-[#F59E0B]'
  return 'text-slate-400'
}

function formatDistance(alert: Alert): string {
  const currentPrice = store.analysis?.current_price || 0
  const distance = Math.abs(alert.price - currentPrice)
  const percentage = (distance / currentPrice) * 100

  if (distance < 1) return '$0.50 以内'
  if (percentage < 0.5) return `${percentage.toFixed(2)}%`

  return `$${distance.toFixed(2)} (${percentage.toFixed(2)}%)`
}

function calculateProgress(alert: Alert): number {
  const currentPrice = store.analysis?.current_price || 0
  const distance = Math.abs(alert.price - currentPrice)
  const percentage = (distance / currentPrice) * 100
  return Math.min(Math.max(100 - percentage * 10, 5), 100)
}

function getProgressClass(alert: Alert) {
  const currentPrice = store.analysis?.current_price || 0
  const distance = Math.abs(alert.price - currentPrice)

  if (distance < 5) return 'bg-emerald-500'
  if (distance < 15) return 'bg-[#F59E0B]'
  return 'bg-slate-500'
}

function formatDate(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  return `${days} 天前`
}
</script>

<style scoped>
.fade-in-up {
  animation: fade-in-up 0.3s ease-out;
}

/* Ensure smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>
