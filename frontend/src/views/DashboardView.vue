<template>
  <div class="min-h-screen bg-[#0F172A]">
    <!-- Header -->
    <header class="sticky top-0 z-20 glass border-b border-slate-700/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-[#F8FAFC]">黄金交易 Agent</h1>
            <div class="flex items-center gap-2 mt-1">
              <span class="status-dot status-dot-positive"></span>
              <p class="text-sm text-slate-400">
                金价刷新时间: {{ priceRefreshTime }}
              </p>
            </div>
          </div>
          <button
            @click="handleRefresh"
            :disabled="store.loading"
            class="btn btn-primary flex items-center gap-2"
            :class="{ 'opacity-50 cursor-wait': store.loading }"
          >
            <svg v-if="!store.loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ store.loading ? '刷新中...' : '刷新数据' }}
          </button>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="store.loading && !store.analysis" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="relative w-20 h-20 mx-auto mb-6">
          <div class="absolute inset-0 border-4 border-[#F59E0B]/20 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-[#F59E0B] rounded-full animate-spin"></div>
          <div class="absolute inset-2 border-4 border-transparent border-t-[#FBBF24] rounded-full animate-spin" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
        </div>
        <p class="text-slate-400 text-lg">正在加载市场数据...</p>
        <p class="text-slate-500 text-sm mt-2">这可能需要几秒钟</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="card bg-red-900/20 border-red-800">
        <div class="flex items-start gap-3">
          <svg class="w-6 h-6 text-red-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="flex-1">
            <p class="text-red-400 font-medium mb-3">数据加载失败</p>
            <p class="text-slate-300 mb-4">{{ store.error }}</p>
            <button @click="store.fetchAnalysis()" class="btn btn-primary">重试</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="store.analysis" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <!-- Signal Card -->
      <section class="card border-l-4" :class="getSignalBorderClass()">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-[#F8FAFC] flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            交易信号
          </h2>
          <span :class="['signal-badge', store.signalLevelClass]">
            {{ signalLabel }}
          </span>
        </div>
        <p class="text-slate-300 leading-relaxed">{{ store.analysis.signal.signal_reason }}</p>
      </section>

      <!-- Price Overview -->
      <section class="kpi-card">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-semibold text-[#F8FAFC]">行情概览</h2>
          <button
            @click="handlePriceRefresh"
            :disabled="priceRefreshing"
            class="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-100 transition-colors cursor-pointer"
            :class="{ 'opacity-50 cursor-wait': priceRefreshing }"
            title="刷新金价"
          >
            <svg
              class="w-4 h-4"
              :class="{ 'animate-spin': priceRefreshing }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30">
            <p class="kpi-label">当前价格</p>
            <p class="kpi-value mono-number mt-2 text-[#F59E0B]">
              ${{ store.analysis.current_price.toFixed(2) }}
            </p>
          </div>
          <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30">
            <p class="kpi-label">价格变化</p>
            <p class="kpi-value mono-number mt-2" :class="store.priceChangeClass">
              {{ store.priceChangeSign }}${{ Math.abs(store.analysis.price_change).toFixed(2) }}
            </p>
          </div>
          <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30">
            <p class="kpi-label">涨跌幅</p>
            <p class="kpi-value mono-number mt-2" :class="store.priceChangeClass">
              {{ store.priceChangeSign }}{{ Math.abs(store.analysis.price_change_pct).toFixed(2) }}%
            </p>
          </div>
        </div>
      </section>

      <!-- Market State -->
      <section class="card">
        <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          市场状态
        </h2>
        <div class="flex items-center gap-4">
          <div class="flex-1 bg-slate-700/30 rounded-lg p-4 border border-slate-600/30">
            <p class="kpi-label">当前模式</p>
            <p class="text-xl font-semibold mt-2 text-[#F8FAFC]">{{ marketStateLabel }}</p>
          </div>
          <div v-if="store.analysis.indicators.trend_dir" class="flex-1 bg-slate-700/30 rounded-lg p-4 border border-slate-600/30">
            <p class="kpi-label">趋势方向</p>
            <p class="text-xl font-semibold mt-2 text-[#F8FAFC]">{{ trendDirectionLabel }}</p>
          </div>
        </div>
      </section>

      <!-- Price Chart -->
      <PriceChart
        :period="store.analysisPeriod"
        @update:period="handlePeriodChange"
      />

      <!-- Key Levels -->
      <section class="card">
        <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          关键价位
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-if="store.analysis.indicators.support_level" class="bg-emerald-900/20 rounded-lg p-3 border border-emerald-700/30">
            <p class="kpi-label text-emerald-400">支撑位</p>
            <p class="text-xl font-mono font-semibold text-emerald-300 mt-2">
              {{ store.analysis.indicators.support_level.toFixed(2) }}
            </p>
          </div>
          <div v-if="store.analysis.indicators.resistance_level" class="bg-red-900/20 rounded-lg p-3 border border-red-700/30">
            <p class="kpi-label text-red-400">阻力位</p>
            <p class="text-xl font-mono font-semibold text-red-300 mt-2">
              {{ store.analysis.indicators.resistance_level.toFixed(2) }}
            </p>
          </div>
          <div v-if="store.analysis.indicators.range_low" class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <p class="kpi-label">区间下沿</p>
            <p class="text-xl font-mono font-semibold text-slate-200 mt-2">
              {{ store.analysis.indicators.range_low.toFixed(2) }}
            </p>
          </div>
          <div v-if="store.analysis.indicators.range_high" class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <p class="kpi-label">区间上沿</p>
            <p class="text-xl font-mono font-semibold text-slate-200 mt-2">
              {{ store.analysis.indicators.range_high.toFixed(2) }}
            </p>
          </div>
        </div>
      </section>

      <!-- Trading Suggestions -->
      <section class="card">
        <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          操作建议
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-[#F59E0B]/10 rounded-lg p-4 border border-[#F59E0B]/30">
            <p class="kpi-label text-[#F59E0B]">建议入场区</p>
            <p class="text-2xl font-mono font-semibold text-[#FBBF24] mt-2">
              {{ store.analysis.signal.entry_zone !== undefined && store.analysis.signal.entry_zone !== null
                ? store.analysis.signal.entry_zone.toFixed(2)
                : '暂无' }}
            </p>
          </div>
          <div class="bg-red-900/20 rounded-lg p-4 border border-red-700/30">
            <p class="kpi-label text-red-400">建议止损区</p>
            <p class="text-2xl font-mono font-semibold text-red-300 mt-2">
              {{ store.analysis.signal.stop_zone !== undefined && store.analysis.signal.stop_zone !== null
                ? store.analysis.signal.stop_zone.toFixed(2)
                : '暂无' }}
            </p>
          </div>
          <div class="bg-emerald-900/20 rounded-lg p-4 border border-emerald-700/30">
            <p class="kpi-label text-emerald-400">建议目标区</p>
            <p class="text-2xl font-mono font-semibold text-emerald-300 mt-2">
              {{ store.analysis.signal.target_zone !== undefined && store.analysis.signal.target_zone !== null
                ? store.analysis.signal.target_zone.toFixed(2)
                : '暂无' }}
            </p>
          </div>
        </div>
      </section>

      <!-- Position & Risk -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Position Suggestion -->
        <div class="kpi-card">
          <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
            </svg>
            仓位建议
          </h2>
          <p class="text-3xl font-bold mt-2" :class="positionLevelClass">
            {{ positionLevelLabel }}
          </p>
        </div>

        <!-- Risk Warning -->
        <div v-if="store.analysis.signal.risk_warning" class="kpi-card bg-gradient-to-br from-orange-900/30 to-orange-800/20 border-orange-700/50">
          <h2 class="text-lg font-semibold text-orange-400 mb-2 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            风险提示
          </h2>
          <p class="text-slate-300 leading-relaxed">{{ store.analysis.signal.risk_warning }}</p>
        </div>
      </section>

      <!-- News Events -->
      <section class="grid grid-cols-1 gap-6">
        <div v-if="store.analysis.news_items && store.analysis.news_items.length > 0" class="card">
          <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            新闻事件
          </h2>

          <div class="space-y-3">
            <div
              v-for="(news, index) in store.analysis.news_items.slice(0, 5)"
              :key="index"
              class="p-4 rounded-lg bg-slate-700/20 hover:bg-slate-700/40 transition-smooth cursor-pointer border border-slate-700/50 hover:border-slate-600/50 row-hover"
              @click="toggleNewsExpansion(index)"
            >
              <div class="flex items-start gap-3">
                <!-- Sentiment Badge -->
                <span
                  class="shrink-0 text-xs px-2.5 py-1 rounded-md font-medium"
                  :class="getSentimentBadgeClass(news.sentiment)"
                >
                  {{ news.sentiment || '中性' }}
                </span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-[#F8FAFC] font-medium">{{ news.title }}</p>
                  <p class="text-xs text-slate-400 mt-1">{{ news.news_time }}</p>
                  <!-- Impact Reason (影响解读) -->
                  <p v-if="news.reason" class="text-xs text-slate-400 mt-2 italic flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    {{ news.reason }}
                  </p>
                </div>
                <svg
                  class="w-4 h-4 text-slate-500 transition-transform duration-200 shrink-0"
                  :class="{ 'rotate-90': expandedNews.has(index) }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>

              <!-- Expanded content -->
              <div v-if="expandedNews.has(index)" class="mt-3 p-3 bg-slate-900/50 rounded border border-slate-700/50" @click.stop>
                <p v-if="news.content" class="text-sm text-slate-300 leading-relaxed">{{ news.content }}</p>
                <div class="flex items-center gap-4 mt-3">
                  <p v-if="news.source" class="text-xs text-slate-400">来源: {{ news.source }}</p>
                  <a
                    v-if="news.url"
                    :href="news.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-xs text-blue-400 hover:text-blue-300 hover:underline inline-flex items-center gap-1"
                  >
                    阅读全文
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Related Assets (DXY & Real Rate) -->
      <section v-if="store.analysis.dxy_price || store.analysis.real_rate !== null" class="card">
        <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
          关联市场指标
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- DXY Card -->
          <div v-if="store.analysis.dxy_price" class="p-4 rounded-lg bg-slate-700/30 border border-slate-600/30">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-[#F8FAFC]">美元指数 (DXY)</h3>
              <span
                class="text-xs px-2 py-1 rounded font-medium"
                :class="store.analysis.dxy_change_pct! > 0 ? 'bg-red-500/20 text-red-300 border border-red-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'"
              >
                {{ store.analysis.dxy_change_pct! > 0 ? '↑' : '↓' }}
                {{ Math.abs(store.analysis.dxy_change_pct!).toFixed(2) }}%
              </span>
            </div>
            <p class="text-2xl font-bold text-[#F8FAFC] mono-number">{{ store.analysis.dxy_price.toFixed(2) }}</p>
            <p class="text-xs text-slate-400 mt-2 flex items-center gap-1">
              <svg v-if="store.analysis.dxy_change_pct! > 0.5" class="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <svg v-else-if="store.analysis.dxy_change_pct! < -0.5" class="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span v-if="store.analysis.dxy_change_pct! > 0.5">
                美元走强可能对黄金形成压力
              </span>
              <span v-else-if="store.analysis.dxy_change_pct! < -0.5">
                美元走弱可能对黄金形成支撑
              </span>
              <span v-else>
                美元指数相对稳定
              </span>
            </p>
          </div>

          <!-- Real Interest Rate Card -->
          <div v-if="store.analysis.real_rate !== null" class="p-4 rounded-lg bg-slate-700/30 border border-slate-600/30">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-[#F8FAFC]">实际利率</h3>
              <span
                class="text-xs px-2 py-1 rounded font-medium"
                :class="store.analysis.real_rate! > 2 ? 'bg-red-500/20 text-red-300 border border-red-500/30' : store.analysis.real_rate! < 0 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-600/20 text-slate-300 border border-slate-600/30'"
              >
                {{ store.analysis.real_rate! > 2 ? '高' : store.analysis.real_rate! < 0 ? '负' : '中' }}
              </span>
            </div>
            <p class="text-2xl font-bold text-[#F8FAFC] mono-number">{{ store.analysis.real_rate!.toFixed(2) }}%</p>
            <p class="text-xs text-slate-400 mt-1">
              名义利率: {{ store.analysis.nominal_rate?.toFixed(1) }}% - 通胀率: {{ store.analysis.inflation_rate?.toFixed(1) }}%
            </p>
            <p class="text-xs text-slate-400 mt-2 flex items-center gap-1">
              <svg v-if="store.analysis.real_rate! > 2" class="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <svg v-else-if="store.analysis.real_rate! < 0" class="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span v-if="store.analysis.real_rate! > 2">
                实际利率较高可能对黄金形成压力
              </span>
              <span v-else-if="store.analysis.real_rate! < 0">
                负实际利率可能对黄金形成支撑
              </span>
              <span v-else>
                实际利率中性,对黄金影响有限
              </span>
            </p>
          </div>
        </div>
      </section>

      <!-- Explanation -->
      <section class="card">
        <h2 class="text-lg font-semibold text-[#F8FAFC] mb-4 flex items-center justify-between">
          <span class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            市场解读
          </span>
          <span
            v-if="store.analysis.llm_explanation"
            class="text-xs px-2.5 py-1 bg-[#8B5CF6]/20 text-[#A78BFA] rounded-md border border-[#8B5CF6]/30 flex items-center gap-1"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            AI 增强
          </span>
        </h2>
        <div
          class="text-slate-300 leading-relaxed prose prose-invert prose-sm max-w-none"
          v-html="formatExplanation(store.analysis.llm_explanation || store.analysis.explanation)"
        ></div>
      </section>

      <!-- Navigation -->
      <div class="flex justify-center gap-4 py-6">
        <router-link to="/chat" class="btn btn-primary flex items-center gap-2 hover:shadow-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          询问更多问题
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import PriceChart from '@/components/PriceChart.vue'

const store = useAnalysisStore()

// News expansion state - track which news items are expanded
const expandedNews = ref<Set<number>>(new Set())

// Price refresh state (for button loading)
const priceRefreshing = ref(false)

// Auto-refresh timer
let priceRefreshTimer: ReturnType<typeof setInterval> | null = null

const toggleNewsExpansion = (index: number) => {
  if (expandedNews.value.has(index)) {
    expandedNews.value.delete(index)
  } else {
    expandedNews.value.add(index)
  }
}

const priceRefreshTime = computed(() => {
  // 优先显示金价刷新时间,否则显示完整刷新时间
  const time = store.priceRefreshTime || store.lastRefresh
  if (!time) return '未更新'
  return time.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
})

const signalLabel = computed(() => {
  const labels: Record<string, string> = {
    strong_buy: '强买',
    buy: '买',
    hold: '观望',
    sell: '卖',
    strong_sell: '强卖',
  }
  return labels[store.analysis?.signal.signal_level || 'hold']
})

const marketStateLabel = computed(() => {
  const labels: Record<string, string> = {
    trend: '趋势模式',
    range: '震荡模式',
    unclear: '不清晰',
  }
  return labels[store.analysis?.market_state || 'unclear']
})

const trendDirectionLabel = computed(() => {
  const labels: Record<string, string> = {
    up: '向上',
    down: '向下',
    neutral: '无方向',
  }
  return labels[store.analysis?.indicators.trend_dir || 'neutral'] || '-'
})

const positionLevelLabel = computed(() => {
  const labels: Record<string, string> = {
    high: '较高仓位',
    medium: '中等仓位',
    low: '低仓位/空仓',
  }
  return labels[store.analysis?.signal.position_level || 'low']
})

const positionLevelClass = computed(() => {
  const level = store.analysis?.signal.position_level
  if (level === 'high') return 'text-emerald-400'
  if (level === 'medium') return 'text-[#F59E0B]'
  return 'text-slate-400'
})

// Get signal border class
function getSignalBorderClass() {
  const level = store.analysis?.signal.signal_level
  const borderMap: Record<string, string> = {
    strong_buy: 'border-emerald-500',
    buy: 'border-emerald-400',
    hold: 'border-slate-500',
    sell: 'border-orange-400',
    strong_sell: 'border-red-500',
  }
  return borderMap[level || 'hold'] || 'border-slate-500'
}

// Helper functions for news
function getSentimentEmoji(sentiment: string): string {
  const emojiMap: Record<string, string> = {
    '利多': '📈',
    '利空': '📉',
    '中性': '➡️',
  }
  return emojiMap[sentiment] || '📊'
}

function getSentimentBadgeClass(sentiment: string): string {
  const classMap: Record<string, string> = {
    '利多': 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    '利空': 'bg-red-500/20 text-red-300 border border-red-500/30',
    '中性': 'bg-slate-500/20 text-slate-300 border border-slate-500/30',
  }
  return classMap[sentiment] || classMap['中性']
}

function formatExplanation(content: string): string {
  // First escape HTML to prevent XSS
  const escaped = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')

  // Then apply markdown formatting
  return escaped
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-100 font-semibold">$1</strong>')
    .replace(/\n/g, '<br>')
}

async function handleRefresh() {
  await store.refreshData(true)
}

// 单独刷新金价（不触发全局分析）
async function handlePriceRefresh() {
  priceRefreshing.value = true
  try {
    await store.fetchPriceOnly()
  } finally {
    priceRefreshing.value = false
  }
}

async function handlePeriodChange(period: string) {
  await store.setAnalysisPeriod(period)
}

// 启动10秒自动刷新
function startPriceAutoRefresh() {
  // 立即执行一次
  store.fetchPriceOnly()

  // 每10秒刷新一次金价
  priceRefreshTimer = setInterval(() => {
    store.fetchPriceOnly()
  }, 10000)  // 10秒
}

// 停止自动刷新
function stopPriceAutoRefresh() {
  if (priceRefreshTimer) {
    clearInterval(priceRefreshTimer)
    priceRefreshTimer = null
  }
}

onMounted(() => {
  store.fetchAnalysis()
  startPriceAutoRefresh()
})

onUnmounted(() => {
  stopPriceAutoRefresh()
})
</script>
