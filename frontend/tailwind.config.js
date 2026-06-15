/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        meliuz: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        ink: {
          950: '#0f0f14',
          900: '#16161f',
          800: '#1e1e2a',
          700: '#2a2a3a',
          500: '#6b7280',
          300: '#cbd5e1',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        display: ['"Outfit"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 40px rgba(249, 115, 22, 0.15)',
        card: '0 8px 32px rgba(0, 0, 0, 0.24)',
      },
    },
  },
  plugins: [],
}
