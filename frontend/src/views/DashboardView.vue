<template>
  <div class="dashboard-view">
    <!-- ========================================
         全局提示弹窗 (Tooltip Overlay)
         ======================================== -->
    <Teleport to="body">
      <Transition name="tooltip-fade">
        <div 
          v-if="activeTooltip && tooltipContent[activeTooltip]"
          class="tooltip-overlay"
          :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
          @mouseenter="activeTooltip = activeTooltip"
          @mouseleave="hideTooltip"
        >
          <div class="tooltip-content">
            <div class="tooltip-header">
              <svg class="tooltip-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="tooltip-title">{{ tooltipContent[activeTooltip]?.title }}</span>
            </div>
            <ul class="tooltip-list">
              <li v-for="item in tooltipContent[activeTooltip]?.items" :key="item.label" class="tooltip-item">
                <span class="tooltip-label">{{ item.label }}</span>
                <span class="tooltip-desc">{{ item.desc }}</span>
              </li>
            </ul>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-title">
          <h1 class="page-title">黄金交易 Agent</h1>
          <div class="status-info">
            <span class="status-dot" :class="store.analysis ? 'status-dot-positive' : 'status-dot-neutral'"></span>
            <p class="status-text">
              {{ priceRefreshTime }}
            </p>
          </div>
        </div>
        <!-- 中间状态指示器 -->
        <div v-if="store.analysis" class="header-status-bar">
          <div class="status-chip" :class="headerMarketStateClass">
            <span class="status-chip-dot"></span>
            <span class="status-chip-text">{{ headerMarketStateText }}</span>
          </div>
          <div class="status-chip" :class="headerSignalClass">
            <span class="status-chip-dot"></span>
            <span class="status-chip-text">{{ signalLabel }}</span>
          </div>
          <div class="status-chip status-chip-confidence" :class="confidenceClass">
            <span class="status-chip-text">置信度 {{ store.analysis?.signal.confidence?.toFixed(0) || 0 }}%</span>
          </div>
        </div>
        <div class="header-actions">
          <router-link to="/chat" class="btn btn-cta btn-sm">
            <svg class="icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            AI 助手
          </router-link>
          <button
            @click="handleRefresh"
            :disabled="store.loading"
            class="btn btn-primary btn-sm"
          >
            <svg v-if="!store.loading" class="icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="icon-small icon-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ store.loading ? '刷新...' : '刷新' }}
          </button>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="store.loading && !store.analysis" class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring spinner-ring-1"></div>
          <div class="spinner-ring spinner-ring-2"></div>
          <div class="spinner-ring spinner-ring-3"></div>
        </div>
        <p class="loading-text">正在加载市场数据...</p>
        <p class="loading-subtext">这可能需要几秒钟</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-container">
      <div class="error-card">
        <div class="error-content">
          <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="error-message">
            <p class="error-title">数据加载失败</p>
            <p class="error-description">{{ store.error }}</p>
            <button @click="store.fetchAnalysis()" class="btn btn-primary">重试</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="store.analysis" class="main-content">
      
      <!-- ============================================
           HERO SECTION: 信号 + 价格 核心区域
           ============================================ -->
      <section class="hero-section">
        <!-- 左侧：交易信号 -->
        <div class="hero-signal" :class="getSignalBorderClass()">
          <div class="signal-header">
            <div class="signal-main">
              <span :class="['signal-badge-large', store.signalLevelClass]">
                {{ signalLabel }}
              </span>
              <span v-if="store.analysis.signal.confidence" :class="['confidence-pill', confidenceClass]">
                {{ store.analysis.signal.confidence?.toFixed(0) }}% 置信度
              </span>
              <!-- 信号说明图标 -->
              <button 
                class="info-icon-btn"
                @mouseenter="showTooltip('heroSignal', $event)"
                @mouseleave="hideTooltip"
                @focus="showTooltip('heroSignal', $event)"
                @blur="hideTooltip"
              >
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </div>
            <p class="signal-reason">{{ store.analysis.signal.signal_reason }}</p>
          </div>
          
          <!-- 综合评分 (紧凑版) -->
          <div v-if="store.analysis.signal.composite_score !== undefined" class="signal-score">
            <div class="score-compact" :class="compositeScoreClass">
              <span class="score-number">{{ store.analysis.signal.composite_score?.toFixed(0) }}</span>
              <span class="score-label-small">综合评分</span>
            </div>
            <div class="score-breakdown">
              <div class="score-item">
                <span class="score-item-label">技术</span>
                <span class="score-item-value" :class="(store.analysis.signal.technical_score || 0) >= 0 ? 'positive' : 'negative'">
                  {{ store.analysis.signal.technical_score?.toFixed(0) || 0 }}
                </span>
              </div>
              <div class="score-item">
                <span class="score-item-label">情感</span>
                <span class="score-item-value" :class="(store.analysis.signal.sentiment_score || 0) >= 0 ? 'positive' : 'negative'">
                  {{ store.analysis.signal.sentiment_score?.toFixed(0) || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：实时价格 -->
        <div class="hero-prices">
          <div class="price-header-row">
            <h3 class="price-section-title">
              实时行情
              <button 
                class="info-icon-btn info-icon-inline"
                @mouseenter="showTooltip('heroPrices', $event)"
                @mouseleave="hideTooltip"
                @focus="showTooltip('heroPrices', $event)"
                @blur="hideTooltip"
              >
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </h3>
            <button
              @click="handlePriceRefresh"
              :disabled="priceRefreshing"
              class="refresh-btn"
              title="刷新金价"
            >
              <svg :class="{ 'icon-spin': priceRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          
          <div class="price-cards-row">
            <!-- 伦敦金 -->
            <div class="price-tile price-tile-gold" :class="{ 'price-update': priceJustUpdated }">
              <div class="price-tile-header">
                <span class="price-market">伦敦金</span>
                <span class="price-source-tag">
                  {{ displayLondonGold?.data_source || 'COMEX' }}
                  <span v-if="isLondonGoldCached" class="cache-badge" title="使用缓存数据">缓存</span>
                </span>
              </div>
              <div class="price-tile-value">
                ${{ displayLondonGold?.price 
                  ? displayLondonGold.price.toFixed(2) 
                  : store.analysis.current_price.toFixed(2) }}
              </div>
              <div class="price-tile-change" v-if="displayLondonGold?.change !== undefined">
                <span :class="(displayLondonGold?.change || 0) >= 0 ? 'up' : 'down'">
                  {{ (displayLondonGold?.change || 0) >= 0 ? '↑' : '↓' }}
                  {{ Math.abs(displayLondonGold?.change || 0).toFixed(2) }}
                  ({{ (displayLondonGold?.change_pct || 0) >= 0 ? '+' : '' }}{{ displayLondonGold?.change_pct?.toFixed(2) }}%)
                </span>
              </div>
              <div class="price-tile-loading" v-else-if="!displayLondonGold">
                获取中...
              </div>
            </div>

            <!-- 上海金 -->
            <div class="price-tile price-tile-shanghai" :class="{ 'price-update': priceJustUpdated }">
              <div class="price-tile-header">
                <span class="price-market">上海金</span>
                <span class="price-source-tag">
                  {{ displayAU9999?.data_source || 'SGE' }}
                  <span v-if="isAU9999Cached" class="cache-badge" title="使用缓存数据">缓存</span>
                </span>
              </div>
              <div class="price-tile-value">
                {{ displayAU9999?.price
                  ? '¥' + displayAU9999.price.toFixed(2)
                  : '获取中...' }}
              </div>
              <div class="price-tile-change" v-if="displayAU9999?.change !== undefined">
                <span :class="(displayAU9999?.change || 0) >= 0 ? 'up' : 'down'">
                  {{ (displayAU9999?.change || 0) >= 0 ? '↑' : '↓' }}
                  {{ Math.abs(displayAU9999?.change || 0).toFixed(2) }}
                  ({{ (displayAU9999?.change_pct || 0) >= 0 ? '+' : '' }}{{ displayAU9999?.change_pct?.toFixed(2) }}%)
                </span>
              </div>
              <div class="price-tile-loading" v-else-if="!displayAU9999">
                获取中...
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ============================================
           市场状态 + 因子分析 双栏布局
           ============================================ -->
      <div class="analysis-grid">
        <!-- 左侧：市场状态 -->
        <section class="card card-glass">
          <h2 class="card-title">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            市场状态
            <button 
              class="info-icon-btn info-icon-inline"
              @mouseenter="showTooltip('marketState', $event)"
              @mouseleave="hideTooltip"
              @focus="showTooltip('marketState', $event)"
              @blur="hideTooltip"
            >
              <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </h2>
          
          <!-- 主状态显示 -->
          <div class="state-hero" :class="getMarketStateClass()">
            <span class="state-hero-text">{{ marketStateLabel }}</span>
          </div>
          
          <!-- 状态指标网格 -->
          <div class="state-metrics">
            <div v-if="store.analysis.indicators.trend_dir" class="metric-item">
              <span class="metric-label">趋势方向</span>
              <span class="metric-value">{{ trendDirectionLabel }}</span>
            </div>
            <div v-if="store.analysis.indicators.adx" class="metric-item">
              <span class="metric-label">趋势强度</span>
              <span class="metric-value">{{ adxDescription }}</span>
            </div>
            <div v-if="store.analysis.indicators.vol_state" class="metric-item">
              <span class="metric-label">波动性</span>
              <span class="metric-value">{{ store.analysis.indicators.vol_state === 'high' ? '高' : store.analysis.indicators.vol_state === 'low' ? '低' : '中等' }}</span>
            </div>
          </div>
        </section>

        <!-- 右侧：因子详情 -->
        <section v-if="store.analysis.signal.factor_details" class="card card-glass">
          <h2 class="card-title">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            </svg>
            因子分析
            <button 
              class="info-icon-btn info-icon-inline"
              @mouseenter="showTooltip('factorAnalysis', $event)"
              @mouseleave="hideTooltip"
              @focus="showTooltip('factorAnalysis', $event)"
              @blur="hideTooltip"
            >
              <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </h2>
          
          <div class="factor-details-list">
            <div 
              v-for="(detail, key) in store.analysis.signal.factor_details" 
              :key="key"
              class="factor-detail-item"
            >
              <div class="factor-detail-header">
                <span class="factor-detail-name">{{ getFactorName(key as string) }}</span>
                <span 
                  class="factor-detail-score" 
                  :class="(detail.score || 0) >= 0 ? 'positive' : 'negative'"
                >
                  {{ ((detail.score || 0) * 100).toFixed(0) }}
                </span>
              </div>
              <div class="factor-detail-bar">
                <div 
                  class="factor-detail-bar-fill" 
                  :class="(detail.score || 0) >= 0 ? 'positive' : 'negative'"
                  :style="{ width: `${Math.min(Math.abs((detail.score || 0) * 100), 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Technical Indicators Detail (新增) -->
      <section class="card card-glass">
        <h2 class="card-title">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
          技术指标详情
        </h2>
        
        <div class="indicators-grid">
          <!-- RSI -->
          <div v-if="store.analysis.indicators.rsi" class="indicator-card">
            <div class="indicator-header">
              <span class="indicator-name">
                RSI (相对强弱)
                <button 
                  class="info-icon-btn info-icon-mini"
                  @mouseenter="showTooltip('indicatorRSI', $event)"
                  @mouseleave="hideTooltip"
                  @focus="showTooltip('indicatorRSI', $event)"
                  @blur="hideTooltip"
                >
                  <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              </span>
              <span class="indicator-value" :class="store.analysis.indicators.rsi > 70 ? 'negative' : store.analysis.indicators.rsi < 30 ? 'positive' : ''">
                {{ store.analysis.indicators.rsi?.toFixed(1) }}
              </span>
            </div>
            <div class="indicator-bar-container">
              <div class="indicator-zones">
                <div class="zone zone-oversold">超卖</div>
                <div class="zone zone-neutral">中性</div>
                <div class="zone zone-overbought">超买</div>
              </div>
              <div 
                class="indicator-pointer"
                :style="{ left: `${store.analysis.indicators.rsi}%` }"
              ></div>
            </div>
            <p class="indicator-desc">{{ rsiDescription }}</p>
          </div>

          <!-- MACD -->
          <div v-if="store.analysis.indicators.macd !== undefined" class="indicator-card">
            <div class="indicator-header">
              <span class="indicator-name">
                MACD
                <button 
                  class="info-icon-btn info-icon-mini"
                  @mouseenter="showTooltip('indicatorMACD', $event)"
                  @mouseleave="hideTooltip"
                  @focus="showTooltip('indicatorMACD', $event)"
                  @blur="hideTooltip"
                >
                  <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              </span>
              <span class="indicator-value" :class="(store.analysis.indicators.macd || 0) >= 0 ? 'positive' : 'negative'">
                {{ store.analysis.indicators.macd?.toFixed(2) }}
              </span>
            </div>
            <div class="macd-details">
              <div class="macd-row">
                <span>信号线:</span>
                <span>{{ store.analysis.indicators.macd_signal?.toFixed(2) }}</span>
              </div>
              <div class="macd-row">
                <span>柱状图:</span>
                <span :class="(store.analysis.indicators.macd_hist || 0) >= 0 ? 'positive' : 'negative'">
                  {{ store.analysis.indicators.macd_hist?.toFixed(2) }}
                </span>
              </div>
              <div v-if="store.analysis.indicators.macd_cross && store.analysis.indicators.macd_cross !== 'none'" class="macd-cross">
                <span :class="store.analysis.indicators.macd_cross === 'golden' ? 'positive' : 'negative'">
                  {{ macdCrossDescription }}
                </span>
              </div>
            </div>
          </div>

          <!-- Bollinger Bands -->
          <div v-if="store.analysis.indicators.bb_upper" class="indicator-card">
            <div class="indicator-header">
              <span class="indicator-name">
                布林带
                <button 
                  class="info-icon-btn info-icon-mini"
                  @mouseenter="showTooltip('indicatorBB', $event)"
                  @mouseleave="hideTooltip"
                  @focus="showTooltip('indicatorBB', $event)"
                  @blur="hideTooltip"
                >
                  <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              </span>
              <span class="indicator-value">宽度 {{ store.analysis.indicators.bb_width?.toFixed(1) }}%</span>
            </div>
            <div class="bb-levels">
              <div class="bb-level">
                <span class="bb-label">上轨</span>
                <span class="bb-value">{{ store.analysis.indicators.bb_upper?.toFixed(2) }}</span>
              </div>
              <div class="bb-level">
                <span class="bb-label">中轨</span>
                <span class="bb-value">{{ store.analysis.indicators.bb_middle?.toFixed(2) }}</span>
              </div>
              <div class="bb-level">
                <span class="bb-label">下轨</span>
                <span class="bb-value">{{ store.analysis.indicators.bb_lower?.toFixed(2) }}</span>
              </div>
            </div>
            <p class="indicator-desc">位置: {{ bbPositionDescription }}</p>
          </div>

          <!-- ADX Direction -->
          <div v-if="store.analysis.indicators.plus_di" class="indicator-card">
            <div class="indicator-header">
              <span class="indicator-name">
                方向指标 (DI)
                <button 
                  class="info-icon-btn info-icon-mini"
                  @mouseenter="showTooltip('indicatorDI', $event)"
                  @mouseleave="hideTooltip"
                  @focus="showTooltip('indicatorDI', $event)"
                  @blur="hideTooltip"
                >
                  <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              </span>
            </div>
            <div class="di-details">
              <div class="di-row">
                <span class="positive">+DI (多方):</span>
                <span class="positive">{{ store.analysis.indicators.plus_di?.toFixed(1) }}</span>
              </div>
              <div class="di-row">
                <span class="negative">-DI (空方):</span>
                <span class="negative">{{ store.analysis.indicators.minus_di?.toFixed(1) }}</span>
              </div>
              <p class="di-conclusion">
                {{ (store.analysis.indicators.plus_di || 0) > (store.analysis.indicators.minus_di || 0) ? '多方占优' : (store.analysis.indicators.plus_di || 0) < (store.analysis.indicators.minus_di || 0) ? '空方占优' : '多空均衡' }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Price Chart -->
      <PriceChart
        :period="store.analysisPeriod"
        @update:period="handlePeriodChange"
      />

      <!-- Market Depth -->
      <MarketDepth />

      <!-- ============================================
           交易建议综合区域：关键价位 + 操作建议 + 仓位/风险
           ============================================ -->
      <section class="card card-glass trading-panel">
        <h2 class="card-title">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          交易建议
        </h2>

        <div class="trading-grid">
          <!-- 操作建议 -->
          <div class="trading-section">
            <h3 class="section-subtitle">
              操作价位
              <button 
                class="info-icon-btn info-icon-mini"
                @mouseenter="showTooltip('tradeLevels', $event)"
                @mouseleave="hideTooltip"
                @focus="showTooltip('tradeLevels', $event)"
                @blur="hideTooltip"
              >
                <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </h3>
            <div class="trade-levels">
              <div class="trade-level entry">
                <span class="trade-level-label">入场区</span>
                <span class="trade-level-value">
                  {{ store.analysis.signal.entry_zone?.toFixed(2) || '-' }}
                </span>
              </div>
              <div class="trade-level stop">
                <span class="trade-level-label">止损区</span>
                <span class="trade-level-value">
                  {{ store.analysis.signal.stop_zone?.toFixed(2) || '-' }}
                </span>
              </div>
              <div class="trade-level target">
                <span class="trade-level-label">目标区</span>
                <span class="trade-level-value">
                  {{ store.analysis.signal.target_zone?.toFixed(2) || '-' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 关键价位 -->
          <div class="trading-section">
            <h3 class="section-subtitle">
              关键价位
              <button 
                class="info-icon-btn info-icon-mini"
                @mouseenter="showTooltip('keyLevels', $event)"
                @mouseleave="hideTooltip"
                @focus="showTooltip('keyLevels', $event)"
                @blur="hideTooltip"
              >
                <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </h3>
            <div class="key-levels">
              <div v-if="store.analysis.indicators.support_level" class="key-level support">
                <span class="key-level-label">支撑</span>
                <span class="key-level-value">{{ store.analysis.indicators.support_level.toFixed(2) }}</span>
              </div>
              <div v-if="store.analysis.indicators.resistance_level" class="key-level resistance">
                <span class="key-level-label">阻力</span>
                <span class="key-level-value">{{ store.analysis.indicators.resistance_level.toFixed(2) }}</span>
              </div>
              <div v-if="store.analysis.indicators.range_low" class="key-level range">
                <span class="key-level-label">区间</span>
                <span class="key-level-value">
                  {{ store.analysis.indicators.range_low.toFixed(0) }} - {{ store.analysis.indicators.range_high?.toFixed(0) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 仓位与风险 -->
          <div class="trading-section">
            <h3 class="section-subtitle">
              仓位建议
              <button 
                class="info-icon-btn info-icon-mini"
                @mouseenter="showTooltip('positionRisk', $event)"
                @mouseleave="hideTooltip"
                @focus="showTooltip('positionRisk', $event)"
                @blur="hideTooltip"
              >
                <svg class="info-icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </h3>
            <div class="position-display">
              <span class="position-badge" :class="positionLevelClass">
                {{ positionLevelLabel }}
              </span>
            </div>
            <div v-if="store.analysis.signal.risk_warning" class="risk-warning-inline">
              <svg class="icon-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>{{ store.analysis.signal.risk_warning }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- News Events -->
      <section v-if="store.analysis.news_items && store.analysis.news_items.length > 0" class="card">
        <h2 class="card-title">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          新闻事件
        </h2>

        <div class="news-list">
          <div
            v-for="(news, index) in store.analysis.news_items.slice(0, 5)"
            :key="'news-' + index"
            class="news-item"
            @click="toggleNewsExpansion(index)"
          >
            <div class="news-header">
              <span class="news-sentiment" :class="getSentimentBadgeClass(news.sentiment)">
                {{ news.sentiment || '中性' }}
              </span>
              <div class="news-content">
                <p class="news-title">{{ news.title }}</p>
                <p class="news-time">{{ news.news_time }}</p>
                <p v-if="news.reason" class="news-reason">
                  <svg class="icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  {{ news.reason }}
                </p>
              </div>
              <svg class="expand-icon" :class="{ 'expand-icon-expanded': expandedNews.has(index) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>

            <!-- Expanded content -->
            <div v-if="expandedNews.has(index)" class="news-expanded" @click.stop>
              <p v-if="news.content" class="news-full-text">{{ news.content }}</p>
              <div class="news-meta">
                <p v-if="news.source" class="news-source">来源: {{ news.source }}</p>
                <a
                  v-if="news.url"
                  :href="news.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="news-link"
                >
                  阅读全文
                  <svg class="icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Related Assets (DXY & Real Rate) -->
      <section v-if="store.analysis.dxy_price || store.analysis.real_rate !== null" class="card">
        <h2 class="card-title">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3-4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 001 1H5a1 1 0 01-1-1V4z" />
          </svg>
          关联市场指标
        </h2>
        <div class="related-assets-grid">
          <!-- DXY Card -->
          <div v-if="store.analysis.dxy_price" class="asset-card">
            <div class="asset-header">
              <h3 class="asset-title">美元指数 (DXY)</h3>
              <span class="asset-badge" :class="store.analysis.dxy_change_pct! > 0 ? 'negative' : 'positive'">
                {{ store.analysis.dxy_change_pct! > 0 ? '↑' : '↓' }}
                {{ Math.abs(store.analysis.dxy_change_pct!).toFixed(2) }}%
              </span>
            </div>
            <p class="asset-value">{{ store.analysis.dxy_price.toFixed(2) }}</p>
            <p class="asset-description">
              <svg v-if="store.analysis.dxy_change_pct! > 0.5" class="icon-small text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <svg v-else-if="store.analysis.dxy_change_pct! < -0.5" class="icon-small text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else class="icon-small text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span v-if="store.analysis.dxy_change_pct! > 0.5">美元走强可能对黄金形成压力</span>
              <span v-else-if="store.analysis.dxy_change_pct! < -0.5">美元走弱可能对黄金形成支撑</span>
              <span v-else>美元指数相对稳定</span>
            </p>
          </div>

          <!-- Real Interest Rate Card -->
          <div v-if="store.analysis.real_rate !== null" class="asset-card">
            <div class="asset-header">
              <h3 class="asset-title">实际利率</h3>
              <span class="asset-badge" :class="store.analysis.real_rate! > 2 ? 'negative' : store.analysis.real_rate! < 0 ? 'positive' : 'neutral'">
                {{ store.analysis.real_rate! > 2 ? '高' : store.analysis.real_rate! < 0 ? '负' : '中' }}
              </span>
            </div>
            <p class="asset-value">{{ store.analysis.real_rate!.toFixed(2) }}%</p>
            <p class="asset-description-small">
              名义利率: {{ store.analysis.nominal_rate?.toFixed(1) }}% - 通胀率: {{ store.analysis.inflation_rate?.toFixed(1) }}%
            </p>
            <p class="asset-description">
              <svg v-if="store.analysis.real_rate! > 2" class="icon-small text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <svg v-else-if="store.analysis.real_rate! < 0" class="icon-small text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else class="icon-small text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span v-if="store.analysis.real_rate! > 2">实际利率较高可能对黄金形成压力</span>
              <span v-else-if="store.analysis.real_rate! < 0">负实际利率可能对黄金形成支撑</span>
              <span v-else>实际利率中性,对黄金影响有限</span>
            </p>
          </div>
        </div>
      </section>

      <!-- Explanation -->
      <section class="card">
        <h2 class="card-title">
          <span class="title-with-icon">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            市场解读
          </span>
          <span
            v-if="store.analysis.llm_explanation"
            class="ai-badge"
          >
            <svg class="icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            AI 增强
          </span>
        </h2>
        <div
          class="explanation-content"
          v-html="formatExplanation(store.analysis.llm_explanation || store.analysis.explanation)"
        ></div>
      </section>

      <!-- Navigation -->
      <div class="navigation">
        <router-link to="/chat" class="btn btn-primary btn-large">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          询问更多问题
          <svg class="icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
import { apiAnalysis, type GoldPricesResponse } from '@/api'
import PriceChart from '@/components/PriceChart.vue'
import MarketDepth from '@/components/MarketDepth.vue'

const store = useAnalysisStore()

// Gold prices from multiple markets
const goldPrices = ref<GoldPricesResponse | null>(null)

// 缓存上一次成功获取的价格数据（用于请求失败时保留显示）
const lastSuccessfulLondonGold = ref<GoldPricesResponse['london_gold'] | null>(null)
const lastSuccessfulAU9999 = ref<GoldPricesResponse['au9999'] | null>(null)

// News expansion state - track which news items are expanded
const expandedNews = ref<Set<number>>(new Set())

// Price refresh state (for button loading)
const priceRefreshing = ref(false)

// Price update animation state
const priceJustUpdated = ref(false)
let priceAnimationTimer: ReturnType<typeof setTimeout> | null = null

// Auto-refresh timer
let priceRefreshTimer: ReturnType<typeof setInterval> | null = null

// ========================================
// Tooltip 系统
// ========================================
const activeTooltip = ref<string | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })

// 显示提示
const showTooltip = (id: string, event: MouseEvent) => {
  activeTooltip.value = id
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  tooltipPosition.value = {
    x: rect.left + rect.width / 2,
    y: rect.bottom + 8
  }
}

// 隐藏提示
const hideTooltip = () => {
  activeTooltip.value = null
}

// 提示内容配置
const tooltipContent: Record<string, { title: string; items: { label: string; desc: string }[] }> = {
  // Hero 区域 - 交易信号
  heroSignal: {
    title: '交易信号说明',
    items: [
      { label: '信号级别', desc: '基于多因子分析得出的操作建议：强买/买/观望/卖/强卖' },
      { label: '置信度', desc: '信号可靠性评估，70%以上为高置信度，40-70%为中等' },
      { label: '综合评分', desc: '技术面与情绪面的加权综合得分，范围-100到+100' },
      { label: '技术评分', desc: '基于RSI/MACD/ADX等技术指标的综合评分' },
      { label: '情感评分', desc: '基于新闻情绪分析的市场情绪得分' },
    ]
  },
  // Hero 区域 - 实时价格
  heroPrices: {
    title: '实时行情说明',
    items: [
      { label: '伦敦金', desc: '国际现货黄金价格（XAU/USD），单位美元/盎司' },
      { label: '上海金', desc: 'AU9999黄金现货价格，单位人民币/克' },
      { label: '涨跌幅', desc: '相较于前一交易日收盘价的变化' },
      { label: '数据源', desc: '价格数据来源，包括Finnhub/Yahoo/SGE等' },
    ]
  },
  // 市场状态
  marketState: {
    title: '市场状态说明',
    items: [
      { label: '强势上涨', desc: 'ADX>25且+DI显著高于-DI，趋势明确向上' },
      { label: '上涨趋势', desc: '价格处于上升通道，但趋势强度一般' },
      { label: '区间震荡', desc: '价格在支撑和阻力之间波动，无明确方向' },
      { label: '下跌趋势', desc: '价格处于下降通道，-DI占优' },
      { label: '高波动', desc: 'ATR或波动率指标显示市场波动剧烈' },
      { label: '趋势方向', desc: '当前均线系统指示的价格运动方向' },
      { label: '趋势强度', desc: '由ADX指标衡量，>25为趋势确立' },
    ]
  },
  // 因子分析
  factorAnalysis: {
    title: '多因子分析说明',
    items: [
      { label: 'trend (趋势)', desc: '基于均线系统的趋势方向和强度评分' },
      { label: 'momentum (动量)', desc: '基于RSI和动量指标的超买超卖评分' },
      { label: 'macd (MACD)', desc: '基于MACD指标交叉和柱状图的信号评分' },
      { label: 'volatility (波动)', desc: '基于布林带和ATR的波动性评分' },
      { label: 'sentiment (情绪)', desc: '基于新闻分析的市场情绪评分' },
      { label: '评分范围', desc: '-100到+100，正值看多，负值看空' },
    ]
  },
  // 技术指标 - RSI
  indicatorRSI: {
    title: 'RSI 相对强弱指标',
    items: [
      { label: '定义', desc: '衡量价格变动速度和幅度的动量指标' },
      { label: '超买区', desc: 'RSI>70，可能面临回调压力' },
      { label: '中性区', desc: 'RSI在30-70之间，无明显信号' },
      { label: '超卖区', desc: 'RSI<30，可能存在反弹机会' },
      { label: '用法', desc: '结合其他指标判断买卖时机' },
    ]
  },
  // 技术指标 - MACD
  indicatorMACD: {
    title: 'MACD 指数平滑异同移动平均',
    items: [
      { label: 'MACD线', desc: '快速EMA(12)与慢速EMA(26)的差值' },
      { label: '信号线', desc: 'MACD线的9日EMA，用于产生交易信号' },
      { label: '柱状图', desc: 'MACD线与信号线的差值，反映动能强弱' },
      { label: '金叉', desc: 'MACD上穿信号线，看多信号' },
      { label: '死叉', desc: 'MACD下穿信号线，看空信号' },
    ]
  },
  // 技术指标 - 布林带
  indicatorBB: {
    title: '布林带 Bollinger Bands',
    items: [
      { label: '中轨', desc: '20日简单移动平均线(SMA20)' },
      { label: '上轨', desc: '中轨 + 2倍标准差，动态阻力位' },
      { label: '下轨', desc: '中轨 - 2倍标准差，动态支撑位' },
      { label: '带宽', desc: '(上轨-下轨)/中轨×100，反映波动率' },
      { label: '位置', desc: '价格相对布林带的位置，判断超买超卖' },
    ]
  },
  // 技术指标 - ADX/DI
  indicatorDI: {
    title: 'ADX 方向指标系统',
    items: [
      { label: '+DI', desc: '正向方向指标，衡量上涨趋势强度' },
      { label: '-DI', desc: '负向方向指标，衡量下跌趋势强度' },
      { label: 'ADX', desc: '平均方向指数，衡量趋势强弱（不分方向）' },
      { label: '多方占优', desc: '+DI > -DI，上涨动能较强' },
      { label: '空方占优', desc: '-DI > +DI，下跌动能较强' },
    ]
  },
  // 交易建议 - 操作价位
  tradeLevels: {
    title: '操作价位说明',
    items: [
      { label: '入场区', desc: '建议的开仓价格区间，基于技术分析计算' },
      { label: '止损区', desc: '建议的止损价位，控制单笔交易最大亏损' },
      { label: '目标区', desc: '建议的止盈价位，基于支撑阻力计算' },
      { label: '风险提示', desc: '价位仅供参考，实际操作需结合市场情况' },
    ]
  },
  // 交易建议 - 关键价位
  keyLevels: {
    title: '关键价位说明',
    items: [
      { label: '支撑位', desc: '历史形成的价格下方支撑，跌破可能加速下跌' },
      { label: '阻力位', desc: '历史形成的价格上方阻力，突破可能加速上涨' },
      { label: '区间', desc: '当前价格可能波动的范围区间' },
      { label: '用法', desc: '支撑买入、阻力卖出，突破追踪' },
    ]
  },
  // 交易建议 - 仓位
  positionRisk: {
    title: '仓位与风险说明',
    items: [
      { label: '重仓', desc: '信号强且置信度高时，可增加仓位(70-100%)' },
      { label: '标准仓', desc: '常规信号强度，建议标准仓位(40-60%)' },
      { label: '轻仓', desc: '信号弱或不确定性高，建议轻仓操作(10-30%)' },
      { label: '风险警告', desc: '系统检测到的潜在风险因素提示' },
    ]
  },
}

const toggleNewsExpansion = (index: number) => {
  if (expandedNews.value.has(index)) {
    expandedNews.value.delete(index)
  } else {
    expandedNews.value.add(index)
  }
}

const priceRefreshTime = computed(() => {
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

// 检查伦敦金是否使用的是缓存数据
// 只有当本次请求失败(is_available=false)但有缓存可用时才显示缓存标记
const isLondonGoldCached = computed(() => {
  const currentData = goldPrices.value?.london_gold
  // 本次请求成功，不是缓存
  if (currentData?.is_available) return false
  // 本次请求失败，但有缓存数据，显示缓存标记
  return !!lastSuccessfulLondonGold.value
})

// 检查上海金是否使用的是缓存数据
const isAU9999Cached = computed(() => {
  const currentData = goldPrices.value?.au9999
  // 本次请求成功，不是缓存
  if (currentData?.is_available) return false
  // 本次请求失败，但有缓存数据，显示缓存标记
  return !!lastSuccessfulAU9999.value
})

// 显示用的伦敦金数据（本次成功用本次，失败用缓存）
const displayLondonGold = computed(() => {
  if (goldPrices.value?.london_gold?.is_available) {
    return goldPrices.value.london_gold
  }
  return lastSuccessfulLondonGold.value
})

// 显示用的上海金数据（本次成功用本次，失败用缓存）
const displayAU9999 = computed(() => {
  if (goldPrices.value?.au9999?.is_available) {
    return goldPrices.value.au9999
  }
  return lastSuccessfulAU9999.value
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
    strong_bull: '强势上涨 📈',
    bull_trend: '上涨趋势 📈',
    range: '区间震荡 ↔️',
    bear_trend: '下跌趋势 📉',
    strong_bear: '强势下跌 📉',
    high_volatility: '高波动 ⚠️',
    unclear: '不清晰',
    trend: '趋势模式',
  }
  return labels[store.analysis?.market_state || 'unclear']
})

// Header 状态文本（简短）
const headerMarketStateText = computed(() => {
  const labels: Record<string, string> = {
    strong_bull: '强多',
    bull_trend: '多头',
    range: '震荡',
    bear_trend: '空头',
    strong_bear: '强空',
    high_volatility: '高波动',
    unclear: '-',
    trend: '趋势',
  }
  return labels[store.analysis?.market_state || 'unclear']
})

// Header 市场状态样式类
const headerMarketStateClass = computed(() => {
  const state = store.analysis?.market_state
  if (state === 'strong_bull' || state === 'bull_trend') return 'status-chip-bull'
  if (state === 'strong_bear' || state === 'bear_trend') return 'status-chip-bear'
  if (state === 'high_volatility') return 'status-chip-volatile'
  return 'status-chip-neutral'
})

// Header 信号样式类
const headerSignalClass = computed(() => {
  const level = store.analysis?.signal.signal_level
  if (level === 'strong_buy' || level === 'buy') return 'status-chip-bull'
  if (level === 'strong_sell' || level === 'sell') return 'status-chip-bear'
  return 'status-chip-neutral'
})

// 综合评分颜色类
const compositeScoreClass = computed(() => {
  const score = store.analysis?.signal.composite_score
  if (score === undefined || score === null) return 'score-neutral'
  if (score >= 30) return 'score-positive'
  if (score <= -30) return 'score-negative'
  return 'score-neutral'
})

// 置信度颜色类
const confidenceClass = computed(() => {
  const conf = store.analysis?.signal.confidence
  if (conf === undefined || conf === null) return 'confidence-low'
  if (conf >= 70) return 'confidence-high'
  if (conf >= 40) return 'confidence-medium'
  return 'confidence-low'
})

// ADX 趋势强度描述
const adxDescription = computed(() => {
  const adx = store.analysis?.indicators.adx
  if (adx === undefined || adx === null) return '-'
  if (adx < 20) return '无趋势'
  if (adx < 25) return '趋势形成中'
  if (adx < 50) return '趋势确立'
  if (adx < 75) return '强势趋势'
  return '极强趋势'
})

// RSI 状态描述
const rsiDescription = computed(() => {
  const rsi = store.analysis?.indicators.rsi
  if (rsi === undefined || rsi === null) return '-'
  if (rsi < 30) return '超卖'
  if (rsi > 70) return '超买'
  return '中性'
})

// MACD 交叉描述
const macdCrossDescription = computed(() => {
  const cross = store.analysis?.indicators.macd_cross
  if (!cross || cross === 'none') return '-'
  if (cross === 'golden') return '金叉 (看多)'
  if (cross === 'dead') return '死叉 (看空)'
  return '-'
})

// 布林带位置描述
const bbPositionDescription = computed(() => {
  const pos = store.analysis?.indicators.bb_position
  const map: Record<string, string> = {
    above: '突破上轨 (超买)',
    upper: '上半区',
    middle: '中轨附近',
    lower: '下半区',
    below: '突破下轨 (超卖)',
  }
  return map[pos || 'middle'] || '-'
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
  if (level === 'high') return 'position-high'
  if (level === 'medium') return 'position-medium'
  return 'position-low'
})

// Get signal border class
function getSignalBorderClass() {
  const level = store.analysis?.signal.signal_level
  const borderMap: Record<string, string> = {
    strong_buy: 'border-emerald',
    buy: 'border-emerald-light',
    hold: 'border-muted',
    sell: 'border-warning',
    strong_sell: 'border-error',
  }
  return borderMap[level || 'hold'] || 'border-muted'
}

// Get market state class
function getMarketStateClass() {
  const state = store.analysis?.market_state
  const classMap: Record<string, string> = {
    strong_bull: 'state-strong-bull',
    bull_trend: 'state-bull',
    range: 'state-range',
    bear_trend: 'state-bear',
    strong_bear: 'state-strong-bear',
    high_volatility: 'state-volatile',
  }
  return classMap[state || 'unclear'] || ''
}

// Helper functions for news
function getSentimentBadgeClass(sentiment: string): string {
  const classMap: Record<string, string> = {
    '利多': 'sentiment-positive',
    '利空': 'sentiment-negative',
    '中性': 'sentiment-neutral',
  }
  return classMap[sentiment] || 'sentiment-neutral'
}

// 因子名称映射
function getFactorName(key: string): string {
  const nameMap: Record<string, string> = {
    trend: '趋势因子',
    momentum: '动量因子',
    volatility: '波动因子',
    support_resistance: '支撑/阻力',
    macro: '宏观调整',
  }
  return nameMap[key] || key
}

function formatExplanation(content: string): string {
  const escaped = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')

  return escaped
    .replace(/\*\*(.*?)\*\*/g, '<strong class="explanation-bold">$1</strong>')
    .replace(/\n/g, '<br>')
}

async function handleRefresh() {
  await store.refreshData(true)
}

// 获取多市场黄金价格（失败时保留上次成功的数据）
async function fetchGoldPrices() {
  try {
    const newData = await apiAnalysis.getGoldPrices()
    
    // 保存原始 API 响应（用于判断本次请求是否成功）
    goldPrices.value = newData
    
    // 只有成功获取时才更新缓存
    if (newData.london_gold?.is_available) {
      lastSuccessfulLondonGold.value = { ...newData.london_gold }
    }
    
    if (newData.au9999?.is_available) {
      lastSuccessfulAU9999.value = { ...newData.au9999 }
    }
  } catch (error) {
    console.error('Failed to fetch gold prices:', error)
    // 完全请求失败时，保留现有数据不变（goldPrices.value 不更新）
  }
}

// 单独刷新金价（不触发全局分析）
async function handlePriceRefresh() {
  priceRefreshing.value = true
  try {
    await Promise.all([
      store.fetchPriceOnly(),
      fetchGoldPrices()
    ])
    triggerPriceAnimation()
  } finally {
    priceRefreshing.value = false
  }
}

// 触发价格更新动画
function triggerPriceAnimation() {
  if (priceAnimationTimer) {
    clearTimeout(priceAnimationTimer)
  }

  priceJustUpdated.value = true

  priceAnimationTimer = setTimeout(() => {
    priceJustUpdated.value = false
  }, 600)
}

async function handlePeriodChange(period: string) {
  await store.setAnalysisPeriod(period)
}

// 启动10秒自动刷新
function startPriceAutoRefresh() {
  store.fetchPriceOnly()
  fetchGoldPrices()

  priceRefreshTimer = setInterval(async () => {
    await Promise.all([
      store.fetchPriceOnly(),
      fetchGoldPrices()
    ])
    triggerPriceAnimation()
  }, 10000)
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

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

/* ========================================
   Tooltip 提示弹窗系统
   ======================================== */
.tooltip-overlay {
  position: fixed;
  z-index: 9999;
  transform: translateX(-50%);
  max-width: 360px;
  min-width: 280px;
  pointer-events: auto;
}

.tooltip-content {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip-icon {
  width: 18px;
  height: 18px;
  color: var(--color-cta);
  flex-shrink: 0;
}

.tooltip-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

.tooltip-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.tooltip-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--spacing-xs) 0;
}

.tooltip-item:not(:last-child) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: var(--spacing-xs);
}

.tooltip-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-cta);
}

.tooltip-desc {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Tooltip 动画 */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: all 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}

/* Info 图标按钮 */
.info-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  cursor: help;
  transition: all var(--transition-fast) var(--ease-default);
  color: var(--color-text-muted);
  vertical-align: middle;
}

.info-icon-btn:hover {
  color: var(--color-cta);
  background: rgba(245, 158, 11, 0.1);
}

.info-icon-btn:focus {
  outline: none;
  color: var(--color-cta);
}

.info-icon-inline {
  margin-left: var(--spacing-xs);
}

.info-icon-mini {
  padding: 2px;
  margin-left: 4px;
}

.info-icon {
  width: 16px;
  height: 16px;
}

.info-icon-sm {
  width: 14px;
  height: 14px;
}

/* ========================================
   基础布局
   ======================================== */
.dashboard-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
  background-attachment: fixed;
}

/* ========================================
   Header - 毛玻璃顶栏
   ======================================== */
.dashboard-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  background: rgba(15, 23, 42, 0.85);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  flex: 1;
}

.page-title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0;
  background: linear-gradient(90deg, #F59E0B, #FBBF24);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: 2px;
}

.status-text {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* Header 状态栏 */
.header-status-bar {
  display: none;
  align-items: center;
  gap: var(--spacing-sm);
}

@media (min-width: 768px) {
  .header-status-bar {
    display: flex;
  }
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: var(--text-xs);
  font-weight: 500;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s ease-in-out infinite;
}

.status-chip-bull {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
}

.status-chip-bull .status-chip-dot {
  background: var(--color-success);
  box-shadow: 0 0 6px var(--color-success);
}

.status-chip-bear {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
}

.status-chip-bear .status-chip-dot {
  background: var(--color-error);
  box-shadow: 0 0 6px var(--color-error);
}

.status-chip-volatile {
  color: var(--color-cta);
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
}

.status-chip-volatile .status-chip-dot {
  background: var(--color-cta);
  box-shadow: 0 0 6px var(--color-cta);
}

.status-chip-neutral {
  color: var(--color-text-muted);
  background: rgba(100, 116, 139, 0.15);
  border-color: rgba(100, 116, 139, 0.3);
}

.status-chip-neutral .status-chip-dot {
  background: var(--color-text-muted);
}

.status-chip-confidence {
  padding: 4px 12px;
}

.status-chip-confidence.confidence-high {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
}

.status-chip-confidence.confidence-medium {
  color: var(--color-cta);
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
}

.status-chip-confidence.confidence-low {
  color: var(--color-text-muted);
  background: rgba(100, 116, 139, 0.15);
  border-color: rgba(100, 116, 139, 0.3);
}

/* ========================================
   主内容区
   ======================================== */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.main-content > * + * {
  margin-top: var(--spacing-lg);
}

/* ========================================
   Hero Section - 核心信息区
   ======================================== */
.hero-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(10px);
}

@media (min-width: 1024px) {
  .hero-section {
    grid-template-columns: 1.2fr 1fr;
  }
}

/* Hero Signal - 左侧信号区 */
.hero-signal {
  padding: var(--spacing-lg);
  background: rgba(15, 23, 42, 0.5);
  border-radius: var(--radius-lg);
  border-left: 4px solid var(--color-text-muted);
}

.hero-signal.border-emerald {
  border-left-color: var(--color-success);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(15, 23, 42, 0.5));
}

.hero-signal.border-emerald-light {
  border-left-color: #34D399;
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.08), rgba(15, 23, 42, 0.5));
}

.hero-signal.border-warning {
  border-left-color: var(--color-warning);
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.1), rgba(15, 23, 42, 0.5));
}

.hero-signal.border-error {
  border-left-color: var(--color-error);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(15, 23, 42, 0.5));
}

.signal-header {
  margin-bottom: var(--spacing-md);
}

.signal-main {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.signal-badge-large {
  font-size: var(--text-2xl);
  font-weight: 700;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  animation: pulse 2s ease-in-out infinite;
}

.confidence-pill {
  font-size: var(--text-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 9999px;
  font-weight: 500;
}

.confidence-high {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.confidence-medium {
  background: rgba(245, 158, 11, 0.2);
  color: var(--color-cta);
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.confidence-low {
  background: rgba(100, 116, 139, 0.2);
  color: var(--color-text-muted);
  border: 1px solid rgba(100, 116, 139, 0.4);
}

.signal-reason {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Signal Score Compact */
.signal-score {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.score-compact {
  text-align: center;
  padding: var(--spacing-md);
  background: rgba(15, 23, 42, 0.5);
  border-radius: var(--radius-md);
  min-width: 80px;
}

.score-compact.score-positive {
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.score-compact.score-negative {
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.score-compact.score-neutral {
  border: 1px solid rgba(100, 116, 139, 0.4);
}

.score-number {
  font-size: var(--text-2xl);
  font-weight: 700;
  font-family: var(--font-mono);
  display: block;
}

.score-compact.score-positive .score-number {
  color: var(--color-success);
}

.score-compact.score-negative .score-number {
  color: var(--color-error);
}

.score-compact.score-neutral .score-number {
  color: var(--color-text-muted);
}

.score-label-small {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  display: block;
  margin-top: 2px;
}

.score-breakdown {
  display: flex;
  gap: var(--spacing-lg);
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.score-item-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.score-item-value {
  font-size: var(--text-lg);
  font-weight: 600;
  font-family: var(--font-mono);
}

.score-item-value.positive {
  color: var(--color-success);
}

.score-item-value.negative {
  color: var(--color-error);
}

/* Hero Prices - 右侧价格区 */
.hero-prices {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.price-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.price-section-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.refresh-btn {
  padding: var(--spacing-xs);
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-base) var(--ease-default);
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(30, 41, 59, 0.8);
  color: var(--color-text);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
  display: block;
}

.price-cards-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.price-tile {
  padding: var(--spacing-md);
  background: rgba(15, 23, 42, 0.6);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all var(--transition-base) var(--ease-default);
}

.price-tile:hover {
  border-color: rgba(245, 158, 11, 0.3);
}

.price-tile-gold {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(15, 23, 42, 0.6));
}

.price-tile-shanghai {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(15, 23, 42, 0.6));
}

.price-tile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.price-market {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-cta);
}

.price-source-tag {
  font-size: 10px;
  color: var(--color-text-disabled);
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.price-tile-value {
  font-size: var(--text-xl);
  font-weight: 700;
  font-family: var(--font-mono);
  color: #FBBF24;
  margin: var(--spacing-xs) 0;
}

.price-tile-change {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
}

.price-tile-change .up {
  color: var(--color-success);
}

.price-tile-change .down {
  color: var(--color-error);
}

.price-tile-error,
.price-tile-loading {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 缓存数据标记 */
.cache-badge {
  display: inline-block;
  margin-left: 4px;
  padding: 1px 4px;
  font-size: 9px;
  font-weight: 500;
  color: var(--color-warning);
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 3px;
  vertical-align: middle;
}

.price-update {
  animation: priceFlash 600ms var(--ease-default);
}

@keyframes priceFlash {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

/* ========================================
   Analysis Grid - 市场状态 + 因子分析
   ======================================== */
.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
}

@media (min-width: 768px) {
  .analysis-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.card-glass {
  background: rgba(30, 41, 59, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(10px);
}

.state-hero {
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  text-align: center;
  margin-bottom: var(--spacing-md);
  background: rgba(15, 23, 42, 0.5);
}

.state-hero-text {
  font-size: var(--text-xl);
  font-weight: 700;
}

.state-hero.state-strong-bull {
  border-left: 4px solid var(--color-success);
  background: rgba(16, 185, 129, 0.15);
}

.state-hero.state-strong-bull .state-hero-text {
  color: var(--color-success);
}

.state-hero.state-bull {
  border-left: 4px solid rgba(16, 185, 129, 0.7);
  background: rgba(16, 185, 129, 0.1);
}

.state-hero.state-bull .state-hero-text {
  color: #34D399;
}

.state-hero.state-range {
  border-left: 4px solid var(--color-text-muted);
  background: rgba(100, 116, 139, 0.15);
}

.state-hero.state-range .state-hero-text {
  color: var(--color-text-muted);
}

.state-hero.state-bear {
  border-left: 4px solid rgba(239, 68, 68, 0.7);
  background: rgba(239, 68, 68, 0.1);
}

.state-hero.state-bear .state-hero-text {
  color: #F87171;
}

.state-hero.state-strong-bear {
  border-left: 4px solid var(--color-error);
  background: rgba(239, 68, 68, 0.15);
}

.state-hero.state-strong-bear .state-hero-text {
  color: var(--color-error);
}

.state-hero.state-volatile {
  border-left: 4px solid var(--color-cta);
  background: rgba(245, 158, 11, 0.15);
}

.state-hero.state-volatile .state-hero-text {
  color: var(--color-cta);
}

.state-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(15, 23, 42, 0.3);
  border-radius: var(--radius-sm);
}

.metric-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.metric-value {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

/* Factor Details List */
.factor-details-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.factor-detail-item {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(15, 23, 42, 0.3);
  border-radius: var(--radius-sm);
}

.factor-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.factor-detail-name {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.factor-detail-score {
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: var(--font-mono);
}

.factor-detail-score.positive {
  color: var(--color-success);
}

.factor-detail-score.negative {
  color: var(--color-error);
}

.factor-detail-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.factor-detail-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.factor-detail-bar-fill.positive {
  background: linear-gradient(90deg, var(--color-success), #34D399);
}

.factor-detail-bar-fill.negative {
  background: linear-gradient(90deg, var(--color-error), #F87171);
}

/* ========================================
   Trading Panel - 交易建议区
   ======================================== */
.trading-panel {
  padding: var(--spacing-lg);
}

.trading-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
}

@media (min-width: 768px) {
  .trading-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.trading-section {
  padding: var(--spacing-md);
  background: rgba(15, 23, 42, 0.4);
  border-radius: var(--radius-md);
}

.section-subtitle {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 var(--spacing-md) 0;
}

.trade-levels {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.trade-level {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
}

.trade-level.entry {
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid var(--color-cta);
}

.trade-level.stop {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid var(--color-error);
}

.trade-level.target {
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid var(--color-success);
}

.trade-level-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.trade-level-value {
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-text);
}

.key-levels {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.key-level {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(15, 23, 42, 0.3);
  border-radius: var(--radius-sm);
}

.key-level.support {
  border-left: 3px solid var(--color-success);
}

.key-level.resistance {
  border-left: 3px solid var(--color-error);
}

.key-level.range {
  border-left: 3px solid var(--color-text-muted);
}

.key-level-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.key-level-value {
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-text);
}

.position-display {
  text-align: center;
  margin-bottom: var(--spacing-md);
}

.position-badge {
  display: inline-block;
  font-size: var(--text-lg);
  font-weight: 700;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
}

.position-badge.position-high {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.position-badge.position-medium {
  background: rgba(245, 158, 11, 0.2);
  color: var(--color-cta);
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.position-badge.position-low {
  background: rgba(100, 116, 139, 0.2);
  color: var(--color-text-muted);
  border: 1px solid rgba(100, 116, 139, 0.4);
}

.risk-warning-inline {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  color: var(--color-warning);
}

.icon-warning {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  margin-top: 1px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto var(--spacing-lg);
}

.spinner-ring {
  position: absolute;
  border-radius: 50%;
  border: 4px solid transparent;
}

.spinner-ring-1 {
  inset: 0;
  border-top-color: rgba(245, 158, 11, 0.2);
}

.spinner-ring-2 {
  inset: 0;
  border-top-color: var(--color-cta);
  animation: spin 1s linear infinite;
}

.spinner-ring-3 {
  inset: 8px;
  border-top-color: #FBBF24;
  animation: spin 1.5s linear infinite reverse;
}

.loading-text {
  font-size: var(--text-lg);
  color: var(--color-text-muted);
  margin: 0;
}

.loading-subtext {
  font-size: var(--text-sm);
  color: var(--color-text-disabled);
  margin: var(--spacing-xs) 0 0 0;
}

/* 错误状态 */
.error-container {
  max-width: 80rem;
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
}

.error-card {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.error-content {
  display: flex;
  gap: var(--spacing-md);
}

.error-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--color-error);
  flex-shrink: 0;
  margin-top: 2px;
}

.error-message {
  flex: 1;
}

.error-title {
  color: var(--color-error);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.error-description {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

/* 信号卡片 */
.signal-card {
  border-left-width: 4px;
  border-left-style: solid;
}

.border-emerald {
  border-left-color: var(--color-success);
}

.border-emerald-light {
  border-left-color: #34D399;
}

.border-warning {
  border-left-color: var(--color-warning);
}

.border-error {
  border-left-color: var(--color-error);
}

.border-muted {
  border-left-color: var(--color-text-muted);
}

.signal-badges {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.signal-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 500;
}

.confidence-high {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.confidence-medium {
  background: rgba(245, 158, 11, 0.2);
  color: var(--color-cta);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.confidence-low {
  background: rgba(100, 116, 139, 0.2);
  color: var(--color-text-muted);
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.signal-description {
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

/* 多因子评分卡片 */
.score-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
}

.score-overview {
  display: flex;
  justify-content: center;
  margin-bottom: var(--spacing-xl);
}

.score-main {
  text-align: center;
  padding: var(--spacing-lg);
  background: rgba(15, 23, 42, 0.5);
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border);
  min-width: 200px;
}

.score-main.score-positive {
  border-color: rgba(16, 185, 129, 0.5);
  background: rgba(16, 185, 129, 0.1);
}

.score-main.score-negative {
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.1);
}

.score-main.score-neutral {
  border-color: rgba(100, 116, 139, 0.5);
}

.score-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-sm);
}

.score-value {
  font-size: var(--text-4xl);
  font-weight: 700;
  font-family: var(--font-mono);
  margin: 0;
}

.score-positive .score-value {
  color: var(--color-success);
}

.score-negative .score-value {
  color: var(--color-error);
}

.score-neutral .score-value {
  color: var(--color-text-muted);
}

.score-bar {
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  margin-top: var(--spacing-md);
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.score-bar-fill.score-positive {
  background: var(--color-success);
}

.score-bar-fill.score-negative {
  background: var(--color-error);
}

.score-bar-fill.score-neutral {
  background: var(--color-text-muted);
}

.factor-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.factor-card {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.factor-name {
  font-size: var(--text-sm);
  color: var(--color-text);
  font-weight: 500;
}

.factor-weight {
  font-size: var(--text-xs);
  color: var(--color-text-disabled);
}

.factor-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  font-family: var(--font-mono);
  margin: 0;
}

.factor-value.positive {
  color: var(--color-success);
}

.factor-value.negative {
  color: var(--color-error);
}

.subfactor-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.subfactor-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(30, 41, 59, 0.3);
  border-radius: var(--radius-sm);
}

.subfactor-name {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  min-width: 100px;
}

.subfactor-bar-container {
  flex: 1;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.subfactor-bar {
  height: 100%;
  border-radius: 3px;
}

.subfactor-bar.positive {
  background: var(--color-success);
}

.subfactor-bar.negative {
  background: var(--color-error);
}

.subfactor-score {
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  min-width: 40px;
  text-align: right;
}

.subfactor-score.positive {
  color: var(--color-success);
}

.subfactor-score.negative {
  color: var(--color-error);
}

/* 市场状态样式 */
.state-strong-bull {
  border-left: 3px solid var(--color-success);
  background: rgba(16, 185, 129, 0.1);
}

.state-bull {
  border-left: 3px solid rgba(16, 185, 129, 0.6);
  background: rgba(16, 185, 129, 0.05);
}

.state-range {
  border-left: 3px solid var(--color-text-muted);
  background: rgba(100, 116, 139, 0.1);
}

.state-bear {
  border-left: 3px solid rgba(239, 68, 68, 0.6);
  background: rgba(239, 68, 68, 0.05);
}

.state-strong-bear {
  border-left: 3px solid var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}

.state-volatile {
  border-left: 3px solid var(--color-cta);
  background: rgba(245, 158, 11, 0.1);
}

/* 技术指标详情样式 */
.indicators-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

@media (max-width: 768px) {
  .indicators-grid {
    grid-template-columns: 1fr;
  }
}

.indicator-card {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.indicator-name {
  font-size: var(--text-sm);
  color: var(--color-text);
  font-weight: 500;
}

.indicator-value {
  font-size: var(--text-lg);
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text);
}

.indicator-value.positive {
  color: var(--color-success);
}

.indicator-value.negative {
  color: var(--color-error);
}

.indicator-bar-container {
  position: relative;
  margin: var(--spacing-md) 0;
}

.indicator-zones {
  display: flex;
  height: 24px;
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.zone {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.7);
}

.zone-oversold {
  flex: 30;
  background: rgba(16, 185, 129, 0.3);
}

.zone-neutral {
  flex: 40;
  background: rgba(100, 116, 139, 0.3);
}

.zone-overbought {
  flex: 30;
  background: rgba(239, 68, 68, 0.3);
}

.indicator-pointer {
  position: absolute;
  top: 0;
  width: 3px;
  height: 24px;
  background: var(--color-text);
  border-radius: 1.5px;
  transform: translateX(-50%);
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
}

.indicator-desc {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
  text-align: center;
}

/* MACD 详情 */
.macd-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.macd-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.macd-row .positive {
  color: var(--color-success);
}

.macd-row .negative {
  color: var(--color-error);
}

.macd-cross {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(30, 41, 59, 0.5);
  border-radius: var(--radius-sm);
  text-align: center;
  font-size: var(--text-sm);
  font-weight: 500;
}

.macd-cross .positive {
  color: var(--color-success);
}

.macd-cross .negative {
  color: var(--color-error);
}

/* 布林带详情 */
.bb-levels {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.bb-level {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
}

.bb-label {
  color: var(--color-text-muted);
}

.bb-value {
  color: var(--color-text);
  font-family: var(--font-mono);
}

/* DI 方向指标 */
.di-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.di-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
}

.di-row .positive {
  color: var(--color-success);
}

.di-row .negative {
  color: var(--color-error);
}

.di-conclusion {
  margin: var(--spacing-sm) 0 0;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(30, 41, 59, 0.5);
  border-radius: var(--radius-sm);
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text);
  font-weight: 500;
}

/* 价格卡片 */
.price-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-lg);
}

@media (min-width: 768px) {
  .price-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.price-card {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(180, 83, 9, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: all var(--transition-base) var(--ease-default);
}

.price-card-gold {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(180, 83, 9, 0.1));
  border-color: rgba(245, 158, 11, 0.3);
}

.price-card-red {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(185, 28, 28, 0.1));
  border-color: rgba(239, 68, 68, 0.3);
}

.price-card:hover {
  border-color: rgba(245, 158, 11, 0.5);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.price-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.price-label {
  font-size: var(--text-sm);
  color: var(--color-cta);
  font-weight: 500;
  margin: 0;
}

.price-source {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.price-value {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: #FBBF24;
  margin: 0;
}

.price-change {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.price-change-value {
  font-size: var(--text-sm);
  font-family: var(--font-mono);
}

.price-change-percent {
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
}

.price-change-value.positive,
.price-change-percent.positive {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.2);
}

.price-change-value.negative,
.price-change-percent.negative {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.2);
}

.price-unit {
  font-size: var(--text-xs);
  color: var(--color-text-disabled);
  margin-top: var(--spacing-sm);
  margin-bottom: 0;
}

/* 价格更新动画 */
.price-update {
  animation: priceFlash 600ms var(--ease-default);
}

@keyframes priceFlash {
  0% {
    background: rgba(245, 158, 11, 0.3);
  }
  100% {
    background: transparent;
  }
}

/* 市场状态 */
.market-state-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-lg);
}

@media (min-width: 640px) {
  .market-state-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.state-card {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.state-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-sm);
}

.state-value {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

/* 关键价位 */
.levels-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 1024px) {
  .levels-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.level-card {
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
}

.level-support {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.level-resistance {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.level-low {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid var(--color-border);
}

.level-high {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid var(--color-border);
}

.level-label {
  font-size: var(--text-sm);
  margin-bottom: var(--spacing-sm);
}

.level-label.positive {
  color: var(--color-success);
}

.level-label.negative {
  color: var(--color-error);
}

.level-value {
  font-size: var(--text-xl);
  font-family: var(--font-mono);
  font-weight: 600;
  margin: 0;
}

.level-value.positive {
  color: var(--color-success-light);
}

.level-value.negative {
  color: var(--color-error-light);
}

/* 操作建议 */
.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .suggestions-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.suggestion-card {
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
}

.suggestion-entry {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.suggestion-stop {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.suggestion-target {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.suggestion-label {
  font-size: var(--text-sm);
  margin-bottom: var(--spacing-sm);
}

.suggestion-label.entry {
  color: var(--color-cta);
}

.suggestion-label.stop {
  color: var(--color-error);
}

.suggestion-label.target {
  color: var(--color-success);
}

.suggestion-value {
  font-size: var(--text-2xl);
  font-family: var(--font-mono);
  font-weight: 600;
  margin: 0;
}

.suggestion-value.entry {
  color: #FBBF24;
}

.suggestion-value.stop {
  color: #F87171;
}

.suggestion-value.target {
  color: #34D399;
}

/* 仓位建议 */
.position-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  margin: 0;
}

.position-high {
  color: var(--color-success);
}

.position-medium {
  color: var(--color-cta);
}

.position-low {
  color: var(--color-text-muted);
}

/* 风险提示 */
.risk-warning-card {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(180, 83, 9, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.card-title-warning {
  color: var(--color-cta);
}

.risk-text {
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

/* 新闻列表 */
.news-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.news-item {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: all var(--transition-base) var(--ease-default);
  cursor: pointer;
}

.news-item:hover {
  background: rgba(30, 41, 59, 0.8);
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.news-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
}

.news-sentiment {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 500;
  border-width: 1px;
  border-style: solid;
  flex-shrink: 0;
}

.sentiment-positive {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success-light);
  border-color: rgba(16, 185, 129, 0.3);
}

.sentiment-negative {
  background: rgba(239, 68, 68, 0.2);
  color: #F87171;
  border-color: rgba(239, 68, 68, 0.3);
}

.sentiment-neutral {
  background: rgba(100, 116, 139, 0.2);
  color: var(--color-text-muted);
  border-color: rgba(100, 116, 139, 0.3);
}

.news-content {
  flex: 1;
  min-width: 0;
}

.news-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  margin: 0;
}

.news-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: var(--spacing-xs) 0 0 0;
}

.news-reason {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--spacing-sm);
  font-style: italic;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.expand-icon {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  color: var(--color-text-disabled);
  transition: transform var(--transition-base) var(--ease-default);
}

.expand-icon-expanded {
  transform: rotate(90deg);
}

.news-expanded {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(15, 23, 42, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.news-full-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.news-source {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.news-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--text-xs);
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast) var(--ease-default);
}

.news-link:hover {
  color: var(--color-primary-light);
  text-decoration: underline;
}

/* 关联市场指标 */
.related-assets-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .related-assets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.asset-card {
  padding: var(--spacing-md);
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.asset-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.asset-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  margin: 0;
}

.asset-badge {
  font-size: var(--text-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.asset-badge.positive {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.asset-badge.negative {
  background: rgba(239, 68, 68, 0.2);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.asset-badge.neutral {
  background: rgba(100, 116, 139, 0.2);
  color: var(--color-text-muted);
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.asset-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text);
  margin: 0;
}

.asset-description {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-sm);
}

.asset-description-small {
  font-size: var(--text-xs);
  color: var(--color-text-disabled);
  margin-top: var(--spacing-xs);
}

/* 市场解读 */
.title-with-icon {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(139, 92, 246, 0.2);
  color: #A78BFA;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(139, 92, 246, 0.3);
  font-size: var(--text-xs);
}

.explanation-content {
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

.explanation-bold {
  color: var(--color-text);
  font-weight: 600;
}

/* 导航 */
.navigation {
  display: flex;
  justify-content: center;
  padding: var(--spacing-xl) 0;
}

.btn-large {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--text-lg);
}

/* 网格布局辅助类 */
.grid-grid-cols-2 {
  display: grid;
  gap: var(--spacing-lg);
  grid-template-columns: repeat(1, 1fr);
}

@media (min-width: 1024px) {
  .grid-grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 图标 */
.icon {
  width: 1.25rem;
  height: 1.25rem;
}

.icon-small {
  width: 0.75rem;
  height: 0.75rem;
}

.icon-spin {
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 按钮图标 */
.icon-btn {
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  background: rgba(30, 41, 59, 0.5);
  color: var(--color-text-muted);
  border: none;
  cursor: pointer;
  transition: all var(--transition-base) var(--ease-default);
}

.icon-btn:hover:not(:disabled) {
  background: var(--color-bg-hover);
  color: var(--color-text);
}

.icon-btn:disabled,
.icon-btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ========================================
   响应式设计
   ======================================== */

/* 平板设备 */
@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
  }
  
  .trading-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .trading-grid .trading-section:last-child {
    grid-column: span 2;
  }
}

/* 移动设备 */
@media (max-width: 768px) {
  .header-content {
    padding: var(--spacing-sm) var(--spacing-md);
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .header-title {
    order: 1;
    flex: 1 1 100%;
  }

  .header-status-bar {
    order: 3;
    flex: 1 1 100%;
    justify-content: flex-start;
    margin-top: var(--spacing-xs);
    display: flex;
    overflow-x: auto;
    padding-bottom: var(--spacing-xs);
  }

  .header-actions {
    order: 2;
    flex: 0 0 auto;
    margin-left: auto;
  }

  .main-content {
    padding: var(--spacing-md);
  }

  .page-title {
    font-size: var(--text-lg);
  }

  .hero-section {
    padding: var(--spacing-md);
  }

  .hero-signal {
    padding: var(--spacing-md);
  }

  .signal-main {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .signal-badge-large {
    font-size: var(--text-xl);
    padding: var(--spacing-xs) var(--spacing-md);
  }

  .signal-score {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .score-breakdown {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .price-cards-row {
    grid-template-columns: 1fr;
  }

  .price-tile-value {
    font-size: var(--text-lg);
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .trading-grid {
    grid-template-columns: 1fr;
  }

  .trading-grid .trading-section:last-child {
    grid-column: span 1;
  }

  .indicator-grid {
    grid-template-columns: 1fr;
  }

  .bb-group {
    grid-column: span 1;
  }

  .btn-sm {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--text-xs);
  }

  .icon-small {
    width: 14px;
    height: 14px;
  }
}

/* 小屏手机 */
@media (max-width: 480px) {
  .main-content {
    padding: var(--spacing-sm);
  }

  .hero-section {
    padding: var(--spacing-sm);
    gap: var(--spacing-sm);
  }

  .card {
    padding: var(--spacing-md);
  }

  .score-compact {
    min-width: 60px;
    padding: var(--spacing-sm);
  }

  .score-number {
    font-size: var(--text-xl);
  }

  .status-chip {
    padding: 3px 8px;
    font-size: 10px;
  }

  .trading-section {
    padding: var(--spacing-sm);
  }

  .trade-level, .key-level {
    padding: var(--spacing-xs) var(--spacing-sm);
  }
}
</style>
