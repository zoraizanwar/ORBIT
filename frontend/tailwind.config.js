/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        orbit: {
          // Dark Workstation Base
          void: '#080C10',
          carbon: '#0B1117',
          slate: '#101820',
          panel: '#131D27',
          border: '#1E293B',
          borderSubtle: '#1E2D3D',

          // Light Workstation Base
          lightBg: '#F8FAFC',
          lightSurface: '#FFFFFF',
          lightPanel: '#F1F5F9',
          lightBorder: '#E2E8F0',
          lightText: '#0F172A',
          lightMuted: '#64748B',

          // Semantic Accent Tokens
          emerald: '#19C37D',
          sky: '#38BDF8',
          water: '#0EA5E9',
          vegetation: '#22C55E',
          urban: '#F59E0B',
          warning: '#F97316',
          critical: '#EF4444',

          // Typography
          text: '#E5E7EB',
          textBright: '#F9FAFB',
          muted: '#94A3B8',
          subtle: '#64748B',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'glow-emerald': '0 0 20px -5px rgba(25, 195, 125, 0.25)',
        'glow-sky': '0 0 20px -5px rgba(56, 189, 248, 0.25)',
        'glow-urban': '0 0 20px -5px rgba(245, 158, 11, 0.25)',
        'glow-critical': '0 0 20px -5px rgba(239, 68, 68, 0.25)',
      },
    },
  },
  plugins: [],
}
