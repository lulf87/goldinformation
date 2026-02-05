<template>
  <div
    :class="cardClasses"
    @click="handleClick"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'elevated' | 'glass' | 'bordered'
  hoverable?: boolean
  clickable?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  hoverable: false,
  clickable: false,
  padding: 'lg',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => {
  const baseClasses = 'card rounded-xl'

  const variantClasses = {
    default: 'card',
    elevated: 'card-elevated',
    glass: 'glass',
    bordered: 'card card-border',
  }

  const paddingClasses = {
    none: '',
    sm: 'p-sm',
    md: 'p-md',
    lg: 'p-lg',
    xl: 'p-xl',
  }

  const classes = [
    baseClasses,
    variantClasses[props.variant],
    paddingClasses[props.padding],
  ]

  if (props.hoverable || props.clickable) {
    classes.push('card-hoverable')
  }

  if (props.clickable) {
    classes.push('cursor-pointer')
  }

  return classes.join(' ')
})

const handleClick = (event: MouseEvent) => {
  if (props.hoverable || props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
/* 基础卡片样式使用设计系统 CSS 变量 */
.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base) var(--ease-default);
}

.card-elevated {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-lg);
}

.card-border {
  border: 1px solid var(--color-border-light);
}

.card-hoverable:hover {
  border-color: var(--color-primary);
  box-shadow: var(--glow-primary), var(--shadow-lg);
  transform: translateY(-2px);
}

.card-hoverable:active {
  transform: translateY(-1px);
}
</style>
