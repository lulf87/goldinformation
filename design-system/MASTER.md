# Gold Trading Agent - 设计系统

## 设计模式
**模式**: Fintech Dashboard（金融交易仪表盘）
- 专业、数据驱动的界面
- 强调信息层次和可读性
- 深色主题为主，突出交易信号

---

## 视觉风格

### 整体风格
- **风格**: 专业金融交易风格
- **关键词**: 专业、可靠、清晰、高效
- **参考**: Bloomberg Terminal、TradingView 的简化版

### 设计原则
1. **数据优先**: 交易信号和关键数据突出显示
2. **可读性**: 使用高对比度确保数据清晰可读
3. **响应式**: 支持桌面和平板访问
4. **性能**: 快速加载，实时更新

---

## 色彩系统

### 主色调（深色主题）
```css
/* 背景色 */
--bg-primary: #0F172A;      /* slate-900 */
--bg-secondary: #1E293B;    /* slate-800 */
--bg-card: #1E293B;         /* slate-800 */

/* 文字色 */
--text-primary: #F1F5F9;    /* slate-100 */
--text-secondary: #94A3B8;  /* slate-400 */
--text-muted: #64748B;      /* slate-500 */

/* 信号色 */
--signal-strong-buy: #10B981;  /* emerald-500 */
--signal-buy: #34D399;         /* emerald-400 */
--signal-hold: #94A3B8;        /* slate-400 */
--signal-sell: #FB923C;        /* orange-400 */
--signal-strong-sell: #EF4444; /* red-500 */

/* 功能色 */
--accent-blue: #3B82F6;     /* blue-500 */
--accent-gold: #F59E0B;     /* amber-500 */
--border-subtle: #334155;   /* slate-700 */
```

### 浅色主题（备用）
```css
/* 背景色 */
--bg-primary: #FFFFFF;
--bg-secondary: #F8FAFC;    /* slate-50 */
--bg-card: #FFFFFF;

/* 文字色 */
--text-primary: #0F172A;    /* slate-900 */
--text-secondary: #475569;  /* slate-600 */
--text-muted: #94A3B8;      /* slate-400 */
```

---

## 字体系统

### 字体选择
- **标题**: Inter、SF Pro Display（系统字体）
- **正文**: Inter、SF Pro Text
- **数字/数据**: SF Mono、Roboto Mono（等宽字体）

### 字体大小
```css
--font-xs: 0.75rem;    /* 12px */
--font-sm: 0.875rem;   /* 14px */
--font-base: 1rem;     /* 16px */
--font-lg: 1.125rem;   /* 18px */
--font-xl: 1.25rem;    /* 20px */
--font-2xl: 1.5rem;    /* 24px */
--font-3xl: 1.875rem;  /* 30px */
```

### 行高
- 标题: 1.2-1.3
- 正文: 1.5-1.6

---

## 组件样式

### 卡片
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.card:hover {
  border-color: var(--accent-blue);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}
```

### 按钮
```css
.btn-primary {
  background: var(--accent-blue);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  transition: all 150ms;
}

.btn-primary:hover {
  background: #2563EB; /* blue-600 */
  transform: translateY(-1px);
}
```

### 信号指示器
```css
.signal-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.signal-strong-buy { background: rgba(16, 185, 129, 0.2); color: var(--signal-strong-buy); }
.signal-buy { background: rgba(52, 211, 153, 0.2); color: var(--signal-buy); }
.signal-hold { background: rgba(148, 163, 184, 0.2); color: var(--signal-hold); }
.signal-sell { background: rgba(251, 146, 60, 0.2); color: var(--signal-sell); }
.signal-strong-sell { background: rgba(239, 68, 68, 0.2); color: var(--signal-strong-sell); }
```

---

## 布局规范

### 容器
```css
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.container-wide {
  max-width: 1600px;
}
```

### 间距
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

---

## 图表配置

### ECharts 主题
```javascript
const tradingTheme = {
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'Inter, SF Pro Display' },
  title: { textStyle: { color: '#F1F5F9' } },
  legend: { textStyle: { color: '#94A3B8' } },
  axisLine: { lineStyle: { color: '#334155' } },
  splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } },
  axisLabel: { color: '#94A3B8' },
};
```

### K 线图配色
```javascript
const candlestickStyle = {
  upColor: '#10B981',
  upBorderColor: '#10B981',
  downColor: '#EF4444',
  downBorderColor: '#EF4444',
};
```

---

## 响应式断点

```css
/* Mobile First */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

---

## 动画规范

```css
/* 微交互 */
.transition-fast {
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
}

.transition-normal {
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* 悬停效果 */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}
```

---

## 图标系统

使用 SVG 图标库：
- **首选**: Heroicons（MIT 许可）
- **备选**: Lucide Icons

图标尺寸：16px、20px、24px、32px

---

## 可访问性

### 对比度要求
- 正文文字: 最小 4.5:1
- 大文字 (18px+): 最小 3:1
- 交互元素: 最小 3:1

### 焦点状态
```css
*:focus-visible {
  outline: 2px solid var(--accent-blue);
  outline-offset: 2px;
}
```

### 触摸目标
- 最小尺寸: 44x44px

---

## 反模式（避免）

| 反模式 | 正确做法 |
|--------|----------|
| 使用 emoji 作为图标 | 使用 SVG 图标 |
| 纯黑色背景 | 使用深蓝灰色（slate-900） |
| 过多颜色（>5 种） | 限制为主色 + 信号色 |
| 低对比度文字 | 确保对比度 ≥4.5:1 |
| 过度动画 | 使用 150-200ms 快速过渡 |
| 悬停时元素位移 | 使用颜色/阴影变化 |
| 固定宽度布局 | 响应式布局 |

---

## 数据展示最佳实践

### 数字格式化
- 价格: 保留 2 位小数（如：2345.67）
- 百分比: 保留 1-2 位小数（如：+2.34%）
- 大数字: 使用 K/M 后缀（如：1.5M）

### 变化指示
```html
<!-- 上涨 -->
<span class="text-green-500">+2.34%</span>

<!-- 下跌 -->
<span class="text-red-500">-1.23%</span>

<!-- 无变化 -->
<span class="text-gray-400">0.00%</span>
```

### 加载状态
```css
.skeleton {
  background: linear-gradient(90deg, #1E293B 25%, #334155 50%, #1E293B 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## Tailwind 配置

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3B82F6',
          600: '#2563EB',
        },
        signal: {
          'strong-buy': '#10B981',
          'buy': '#34D399',
          'hold': '#94A3B8',
          'sell': '#FB923C',
          'strong-sell': '#EF4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'sans-serif'],
        mono: ['SF Mono', 'Roboto Mono', 'monospace'],
      },
    },
  },
};
```
