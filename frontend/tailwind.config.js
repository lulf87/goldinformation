/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // 支持手动切换暗色模式
  theme: {
    extend: {
      colors: {
        // 设计系统主配色
        primary: {
          DEFAULT: '#2563EB', // 蓝色
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        secondary: {
          DEFAULT: '#3B82F6', // 浅蓝
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        cta: {
          DEFAULT: '#F97316', // 橙色 (CTA)
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
          700: '#C2410C',
          800: '#9A3412',
          900: '#7C2D12',
        },
        // 背景色
        background: {
          DEFAULT: '#0F172A', // 深岩灰 (暗色模式主背景)
          light: '#F8FAFC',   // 浅色模式背景
        },
        // 文本色
        text: {
          DEFAULT: '#F8FAFC', // 浅灰白 (暗色模式文本)
          dark: '#1E293B',    // 深色 (浅色模式文本)
          muted: '#94A3B8',   // 静音文本
        },
        // 交易专用配色
        trading: {
          up: '#26A69A',      // 上涨/利好 (绿色)
          down: '#EF5350',    // 下跌/利空 (红色)
          neutral: '#94A3B8', // 中性
        },
        // 信号配色 (保留原有)
        signal: {
          'strong-buy': '#10B981',
          'buy': '#34D399',
          'hold': '#94A3B8',
          'sell': '#FB923C',
          'strong-sell': '#EF4444',
        },
        // Slate 颜色 (扩展)
        slate: {
          750: '#1e293b',
          850: '#0f172a',
          900: '#0f172a',
          950: '#020617',
        },
      },
      fontFamily: {
        // 设计系统字体 - IBM Plex Sans (金融专业)
        sans: [
          'IBM Plex Sans',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        // 等宽字体 (用于数据显示)
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'SF Mono',
          'Roboto Mono',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
      // 自定义间距 (匹配设计系统)
      spacing: {
        'xs': '4px',      // 0.25rem - 紧凑间距
        'sm': '8px',      // 0.5rem - 小间距
        'md': '16px',     // 1rem - 标准间距
        'lg': '24px',     // 1.5rem - 大间距
        'xl': '32px',     // 2rem - 超大间距
        '2xl': '48px',    // 3rem - 段落间距
        '3xl': '64px',    // 4rem - 英雄区块间距
      },
      // 自定义阴影 (匹配设计系统)
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px rgba(0, 0, 0, 0.15)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
        // 焦点环 (无障碍访问)
        'focus': '0 0 0 3px rgba(37, 99, 235, 0.2)',
        'focus-visible': '0 0 0 3px rgba(37, 99, 235, 0.5)',
      },
      // 自定义动画 (匹配设计系统)
      animation: {
        // 脉冲动画 (骨架屏)
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        // 缓慢旋转 (加载中)
        'spin-slow': 'spin 3s linear infinite',
        // 闪烁动画 (实时数据)
        'blink': 'blink 1s ease-in-out infinite',
        // 扫描动画 (交易界面)
        'scan': 'scan 2s linear infinite',
        // 滑入动画 (面板展开)
        'slide-in': 'slideIn 0.3s ease-out',
        // 淡入动画
        'fade-in': 'fadeIn 0.2s ease-out',
        // 轻微上移 (卡片悬停)
        'float-up': 'floatUp 0.2s ease-out',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        scan: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        floatUp: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-2px)' },
        },
      },
      // 过渡时长 (匹配设计系统)
      transitionDuration: {
        '150': '150ms', // 微交互
        '200': '200ms', // 标准过渡
        '300': '300ms', // 中等动画
        '400': '400ms', // 复杂动画
      },
      // 边框半径
      borderRadius: {
        'sm': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '20px',
        'full': '9999px',
      },
      // Z-index 层级 (匹配设计系统)
      zIndex: {
        'dropdown': 10,
        'sticky': 20,
        'fixed': 30,
        'modal-backdrop': 40,
        'modal': 50,
        'popover': 60,
        'tooltip': 70,
      },
    },
  },
  plugins: [],
}
