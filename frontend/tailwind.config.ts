import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#030303", 
          surface: "#0A0A0A", 
          glass: "rgba(10, 10, 10, 0.7)",
        },
        accent: {
          cyan: "#00F0FF", 
          crimson: "#FF003C", 
          emerald: "#00FF94", 
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        "glow-gradient": "radial-gradient(circle at center, rgba(0,240,255,0.05) 0%, transparent 70%)",
      },
      boxShadow: {
        "glow": "0 0 20px rgba(0, 240, 255, 0.15)",
        "neumorph": "inset 1px 1px 1px rgba(255, 255, 255, 0.05), 0 4px 10px rgba(0,0,0,0.5)",
      }
    },
  },
  plugins: [],
};
export default config;