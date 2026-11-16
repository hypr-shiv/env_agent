/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ocean: {
          950: '#030b14',
          900: '#061626',
          850: '#0a2138',
          800: '#0f2c4a',
          700: '#15416b',
          600: '#1b5b94',
          500: '#2378be',
          400: '#389bec',
          300: '#72b8f4',
          200: '#abd5fa',
          100: '#dcebfd',
          50: '#f0f6fe'
        },
        aqua: {
          DEFAULT: '#00d2d3',
          glow: '#54a0ff'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
      }
    },
  },
  plugins: [],
}

