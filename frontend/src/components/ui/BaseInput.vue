<template>
  <div class="input-wrapper">
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="text-trading-down">*</span>
    </label>

    <div class="input-container" :class="{ 'has-icon': $slots.prefix || $slots.suffix }">
      <!-- 前缀图标/插槽 -->
      <div v-if="$slots.prefix" class="input-prefix">
        <slot name="prefix" />
      </div>

      <!-- 输入框 -->
      <input
        :id="inputId"
        ref="inputRef"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        :min="min"
        :max="max"
        :step="step"
        :class="inputClasses"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- 后缀图标/插槽 -->
      <div v-if="$slots.suffix || clearable" class="input-suffix">
        <!-- 清除按钮 -->
        <button
          v-if="clearable && inputValue && !disabled && !readonly"
          class="clear-button"
          @click="handleClear"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <slot name="suffix" />
      </div>
    </div>

    <!-- 帮助文本 / 错误提示 -->
    <div v-if="helpText || error" class="input-help">
      <span v-if="error" class="text-trading-down">{{ error }}</span>
      <span v-else-if="helpText" class="text-text-muted">{{ helpText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'password' | 'email' | 'number' | 'tel'
  label?: string
  placeholder?: string
  helpText?: string
  error?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  clearable?: boolean
  maxlength?: number
  min?: number
  max?: number
  step?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  clear: []
}>()

const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const inputClasses = computed(() => {
  const classes = [
    'input',
    'input-default',
  ]

  if (props.error) {
    classes.push('border-trading-down focus:ring-trading-down')
  }

  if (props.disabled) {
    classes.push('opacity-50 cursor-not-allowed')
  }

  return classes.join(' ')
})

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

// 暴露方法给父组件
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
})
</script>

<style scoped>
.input-wrapper {
  @apply w-full;
}

.input-label {
  @apply block text-sm font-medium mb-2 text-text;
}

.input-container {
  @apply relative flex items-center;
}

.input-container.has-icon .input {
  @apply rounded-l-none rounded-r-lg;
}

.input {
  @apply w-full px-4 py-3 rounded-lg border transition-colors duration-200;
  @apply focus:outline-none focus:ring-2 focus:ring-primary;
}

.input-default {
  @apply border-gray-300 dark:border-gray-600 bg-white dark:bg-background;
  @apply text-text dark:text-text placeholder:text-text-muted;
}

.input-prefix,
.input-suffix {
  @apply flex items-center px-3 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600;
  @apply text-text-muted;
}

.input-prefix {
  @apply rounded-l-lg border-r-0;
}

.input-suffix {
  @apply rounded-r-lg border-l-0;
}

.input-container.has-icon .input {
  @apply rounded-none;
}

.clear-button {
  @apply p-1 hover:text-trading-down transition-colors;
  @apply focus:outline-none focus:ring-2 focus:ring-primary rounded;
}

.input-help {
  @apply mt-2 text-sm;
}
</style>
