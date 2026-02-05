import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: {
        title: '黄金市场分析',
      },
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/views/ChatView.vue'),
      meta: {
        title: 'AI 智能助手',
      },
    },
    {
      path: '/quick-start',
      name: 'quick-start',
      component: () => import('@/views/QuickStart.vue'),
      meta: {
        title: '快速开始',
      },
    },
    {
      path: '/analysis',
      name: 'market-analysis',
      component: () => import('@/views/MarketAnalysisView.vue'),
      meta: {
        title: '深度市场分析',
      },
    },
  ],
})

export default router
