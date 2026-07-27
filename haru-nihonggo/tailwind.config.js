/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        background: '#FAF9F6', // Off-white pastel background
        card: '#FFFFFF',
        mint: '#E8F5E9',
        pink: '#FFEBEE',
        text: '#333333',
        subtext: '#888888',
      }
    },
  },
  plugins: [],
}
