/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        'bento': {
          bg: '#f5f5f7',
          card: '#ffffff',
        },
        'committee': {
          a: '#3b82f6',
          b: '#8b5cf6',
          c: '#f97316',
        },
        'judge': '#f59e0b',
        slate: {
          850: '#1a2332',
        }
      },
      borderRadius: {
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'bento': '0 8px 20px rgba(0,0,0,0.02), 0 4px 8px rgba(0,0,0,0.03)',
        'bento-lg': '0 20px 30px rgba(0,0,0,0.04), 0 8px 12px rgba(0,0,0,0.05)',
      },
      animation: {
        'gradient': 'gradient 8s ease infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        }
      },
    },
  },
  plugins: [],
}
