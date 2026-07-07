import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: "#F5F0E8",
        "cream-dark": "#EDE8DF",
        neo: {
          black: "#0D0D0D",
          yellow: "#FFE500",
          white: "#FFFFFF",
        },
      },
      boxShadow: {
        neo: "4px 4px 0px #0D0D0D",
        "neo-lg": "6px 6px 0px #0D0D0D",
        "neo-sm": "2px 2px 0px #0D0D0D",
        "neo-white": "4px 4px 0px #FFFFFF",
        "neo-white-lg": "6px 6px 0px #FFFFFF",
        "neo-white-sm": "2px 2px 0px #FFFFFF",
      },
      borderWidth: {
        "3": "3px",
      },
    },
  },
  plugins: [],
};

export default config;
