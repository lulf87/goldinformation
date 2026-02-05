<template>
  <button
    :type="nativeType"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>

    <!-- Button Content -->
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'cta' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  nativeType?: 'button' | 'submit' | 'reset'
  block?: boolean
  icon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  nativeType: 'button',
  block: false,
  icon: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'btn inline-flex items-center justify-center font-medium transition-all duration-200 cursor-pointer'

  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    cta: 'btn-cta',
    ghost: 'btn-ghost',
    danger: 'btn-danger',
  }

  const sizeClasses = {
    sm: 'btn-sm',
    md: '',
    lg: 'btn-lg',
  }

  const classes = [
    baseClasses,
    variantClasses[props.variant],
    sizeClasses[props.size],
  ]

  // Icon-only buttons
  if (props.icon) {
    classes.push('p-2')
  }

  // Full width
  if (props.block) {
    classes.push('w-full')
  }

  // Disabled state
  if (props.disabled || props.loading) {
    classes.push('btn-disabled')
  }

  // Loading state
  if (props.loading) {
    classes.push('btn-loading')
  }

  return classes.join(' ')
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
/* 使用设计系统 CSS 变量 */
.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  border: none;
  outline: none;
  font-weight: 500;
  gap: var(--spacing-sm);
  transition: all var(--transition-base) var(--ease-default);
}

/* 焦点状态 */
.btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* 主要按钮 */
.btn-primary {
  background: var(--color-primary);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  box-shadow: var(--glow-primary);
  transform: translateY(-1px);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

/* 次要按钮 */
.btn-secondary {
  background: var(--color-bg-hover);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-bg-elevated);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* CTA 按钮 */
.btn-cta {
  background: var(--color-cta);
  color: #ffffff;
  font-weight: 600;
}

.btn-cta:hover:not(:disabled) {
  background: var(--color-cta-hover);
  box-shadow: var(--glow-warning);
  transform: translateY(-1px);
}

/* 幽灵按钮 */
.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid transparent;
}

.btn-ghost:hover:not(:disabled) {
  background: var(--color-bg-hover);
  color: var(--color-text);
}

/* 危险按钮 */
.btn-danger {
  background: var(--color-error);
  color: #ffffff;
}

.btn-danger:hover:not(:disabled) {
  background: #DC2626;
  box-shadow: var(--glow-error);
}

/* 按钮尺寸 */
.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-sm);
}

.btn-lg {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--text-lg);
}

/* 按钮状态 */
.btn-disabled,
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-loading {
  cursor: wait;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 0.6s linear infinite;
}
</style>
