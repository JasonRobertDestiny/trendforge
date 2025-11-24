/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        midnight: '#0f172a',
        sand: '#f5f0e6',
        accent: '#f97316',
        teal: '#0ea5e9',
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: theme('colors.slate.700'),
            a: {
              color: theme('colors.teal.600'),
              '&:hover': { color: theme('colors.accent') },
            },
            h1: { color: theme('colors.slate.900') },
            h2: { color: theme('colors.slate.900') },
            h3: { color: theme('colors.slate.900') },
            strong: { color: theme('colors.slate.900') },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
