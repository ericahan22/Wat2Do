/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        shine: {
          '0%': { backgroundPosition: '200% 0' },
          '25%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        gradientFlow: {
            '0%': { 'background-position':'0% 50%' },
            '50%': { 'background-position': '100% 50%' },
            '100%': { 'background-position': '0% 50%' },
        },
      },
      animation: {
        shine: 'shine 3s ease-out infinite',
        'gradient-flow': 'gradientFlow 10s ease 0s infinite normal none running',
      },
    },
  },
  plugins: [],
} 