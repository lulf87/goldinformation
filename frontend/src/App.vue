<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  document.title = '黄金交易 Agent - Gold Trading Agent'
})
</script>

<style>
.app-container {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}
</style>
