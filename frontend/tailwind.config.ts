import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        shiomi: {
          bg: '#08090c',
          surface: '#0d0e12',
          blue: '#2563eb',
          text: '#94a3b8',
        },
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        orbitron: ['Orbitron', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
