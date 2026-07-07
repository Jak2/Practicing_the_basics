/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{astro,html,js,ts,jsx,tsx,md,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Light mode
        'docs-bg': '#ffffff',
        'docs-sidebar': '#f8fafc',
        'docs-border': '#e2e8f0',
        'docs-text': '#1e293b',
        'docs-text-muted': '#64748b',
        'docs-accent': '#6366f1',
        'docs-accent-hover': '#4f46e5',
        // Dark mode
        'docs-bg-dark': '#0f172a',
        'docs-sidebar-dark': '#1e293b',
        'docs-border-dark': '#334155',
        'docs-text-dark': '#f1f5f9',
        'docs-text-muted-dark': '#94a3b8',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace'],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: theme('colors.docs-text'),
            a: {
              color: theme('colors.docs-accent'),
              '&:hover': {
                color: theme('colors.docs-accent-hover'),
              },
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            code: {
              backgroundColor: theme('colors.slate.100'),
              padding: '0.25rem 0.375rem',
              borderRadius: '0.25rem',
              fontWeight: '500',
            },
          },
        },
        invert: {
          css: {
            color: theme('colors.docs-text-dark'),
            a: {
              color: theme('colors.indigo.400'),
            },
            code: {
              backgroundColor: theme('colors.slate.800'),
            },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
