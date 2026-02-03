<template>
  <div class="min-h-screen bg-slate-900 flex flex-col">
    <!-- Header -->
    <header class="bg-slate-800 border-b border-slate-700 px-4 py-3">
      <div class="flex items-center gap-4">
        <router-link to="/" class="text-slate-400 hover:text-slate-200 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </router-link>
        <h1 class="text-lg font-semibold text-slate-100">智能问答</h1>
      </div>
    </header>

    <!-- Messages -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
      <!-- Welcome message -->
      <div v-if="messages.length === 0" class="text-center text-slate-400 py-8">
        <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <p class="text-lg mb-2">欢迎使用黄金交易智能问答</p>
        <p class="text-sm">您可以询问：</p>
        <ul class="text-sm mt-2 space-y-1">
          <li>"为什么给出该信号？"</li>
          <li>"当前关键位是什么？"</li>
          <li>"下一步建议如何操作？"</li>
          <li>"近期重要新闻有哪些？"</li>
        </ul>
      </div>

      <!-- Message list -->
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-[80%] rounded-lg px-4 py-2',
            msg.role === 'user'
              ? 'bg-primary text-white'
              : 'bg-slate-800 text-slate-200 border border-slate-700'
          ]"
        >
          <!-- 用户消息使用纯文本,助手消息使用格式化HTML -->
          <div
            v-if="msg.role === 'user'"
            class="whitespace-pre-line"
          >{{ msg.content }}</div>
          <div
            v-else
            class="prose prose-invert prose-sm max-w-none"
            v-html="formatSafeHtml(msg.content)"
          ></div>
          <div v-if="msg.role === 'assistant'" class="mt-2 text-xs text-slate-400">
            {{ suggestedQuestions.length > 0 ? '' : '点击下方问题继续' }}
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="flex justify-start">
        <div class="bg-slate-800 rounded-lg px-4 py-2 border border-slate-700">
          <div class="flex space-x-2">
            <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Suggested Questions -->
    <div v-if="messages.length > 0 && suggestedQuestions.length > 0" class="px-4 py-2 border-t border-slate-700">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="(q, i) in suggestedQuestions"
          :key="i"
          @click="sendMessage(q)"
          class="px-3 py-1 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-full transition-colors"
        >
          {{ q }}
        </button>
      </div>
    </div>

    <!-- Input -->
    <div class="border-t border-slate-700 p-4">
      <form @submit.prevent="sendMessage(inputText)" class="flex gap-2">
        <input
          v-model="inputText"
          type="text"
          placeholder="输入您的问题..."
          class="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-primary"
          :disabled="loading"
        />
        <button
          type="submit"
          :disabled="loading || !inputText.trim()"
          class="btn btn-primary px-6"
          :class="{ 'opacity-50 cursor-wait': loading }"
        >
          发送
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { apiAnalysis } from '@/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputText = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const suggestedQuestions = ref<string[]>([
  '为什么给出该信号？',
  '当前关键位是什么？',
  '下一步建议如何操作？',
  '近期重要新闻有哪些？',
])

async function sendMessage(text?: string) {
  const question = text || inputText.value
  if (!question.trim() || loading.value) return

  // Add user message
  messages.value.push({ role: 'user', content: question })
  inputText.value = ''
  suggestedQuestions.value = []

  // Scroll to bottom
  await nextTick()
  scrollToBottom()

  // Send to API
  loading.value = true
  try {
    const response = await apiAnalysis.sendQuery(question)
    messages.value.push({ role: 'assistant', content: response.answer })
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，处理问题时出错。请稍后再试。'
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function formatSafeHtml(content: string): string {
  // First escape HTML to prevent XSS
  const escaped = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')

  // Then apply markdown formatting
  return escaped
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-200">$1</strong>')
    .replace(/\n/g, '<br>')
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>
