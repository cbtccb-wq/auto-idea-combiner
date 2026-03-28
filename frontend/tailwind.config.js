/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          900: "#020617",
          800: "#0f172a",
          700: "#172554"
        },
        accent: {
          DEFAULT: "#22d3ee",
          soft: "#67e8f9"
        }
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,0.06), 0 20px 60px rgba(15, 23, 42, 0.45)"
      },
      backgroundImage: {
        "app-grid":
          "radial-gradient(circle at 1px 1px, rgba(148,163,184,0.12) 1px, transparent 0)"
      }
    }
  },
  plugins: []
};
