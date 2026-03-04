/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        aurora: {
          50: '#eef6ff',
          100: '#dcecff',
          500: '#4f8ef7',
          700: '#2b66c6',
        },
      },
    },
  },
  plugins: [],
};
