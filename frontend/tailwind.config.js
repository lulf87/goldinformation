/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
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
        // Slate colors for dark theme
        slate: {
          750: '#1e293b',
          850: '#0f172a',
          900: '#0f172a',
          950: '#020617',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Roboto Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
