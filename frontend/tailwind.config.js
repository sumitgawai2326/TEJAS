/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        krishi: {
          dark: '#0f291e',
          forest: '#1b4d3e',
          leaf: '#2d6a4f',
          accent: '#52b788',
          light: '#d8f3dc',
          sand: '#f4f1de',
          clay: '#e07a5f',
          gold: '#e9c46a'
        }
      }
    },
  },
  plugins: [],
}
