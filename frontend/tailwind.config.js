/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          bg: "#14181A",
          surface: "#1C2220",
          surface2: "#242B28",
          border: "#2C3431",
        },
        ink: {
          primary: "#ECE8DE",
          secondary: "#9CA39B",
          faint: "#5C655F",
        },
        blaze: {
          DEFAULT: "#D97742",
          dim: "#A85C32",
          bright: "#E8956A",
        },
        moss: {
          DEFAULT: "#7FA66B",
          dim: "#5C7E4C",
        },
        ochre: {
          DEFAULT: "#D4A017",
          dim: "#A87D12",
        },
        rust: {
          DEFAULT: "#B5533C",
          dim: "#8C3F2D",
        },
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["IBM Plex Sans", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
