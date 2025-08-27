/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class", // allows toggling if you ever want light mode
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#0f0f14",         // main background
          text: "#e5e5f0",       // default text
          surface: "#1a1a22",    // panels, cards, table rows
          accent: "#382259",     // banner purple
          accentHover: "#7c3aed",
          danger: "#dc2626",     // red
          success: "#16a34a",    // green
          muted: "#6b7280",      // gray for borders/hints
        }
      }
    }
  },
  plugins: [],
}
