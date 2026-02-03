<template>
  <div id="app" class="min-h-screen bg-slate-900">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  document.title = '黄金交易 Agent - Gold Trading Agent'
})
</script>
