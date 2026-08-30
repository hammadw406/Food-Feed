import type { Config } from "tailwindcss";

/**
 * Design tokens translated from the mobile reference / approved Phase 1 spec.
 * Warm paper ground, ember action accent, saffron for discovery, basil for
 * positive signal. No gradients-as-decoration; soft borders + small shadows.
 */
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F7F2E9",
        board: "#EFE7D7",
        surface: "#FFFFFF",
        "surface-2": "#F4EDE0",
        hairline: "#E7DDCB",
        ink: "#221D17",
        "ink-2": "#6A5F51",
        "ink-3": "#9C8F7C",
        ember: {
          DEFAULT: "#DE4A1E",
          hover: "#C63F17",
          soft: "#FBE6DC",
        },
        saffron: { DEFAULT: "#E29A32", soft: "#F8ECD5" },
        basil: { DEFAULT: "#3B7A54", soft: "#E0EDE2" },
        plum: "#5A2E40",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        card: "22px",
        xl2: "28px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 2px 6px rgba(34,29,23,.05), 0 14px 34px rgba(34,29,23,.09)",
        soft: "0 1px 2px rgba(34,29,23,.06), 0 4px 14px rgba(34,29,23,.06)",
        pop: "0 12px 40px rgba(34,29,23,.18)",
      },
      maxWidth: {
        shell: "1440px",
        content: "1120px",
      },
    },
  },
  plugins: [],
};

export default config;
