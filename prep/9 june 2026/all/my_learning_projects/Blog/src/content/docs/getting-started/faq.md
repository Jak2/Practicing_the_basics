---
title: FAQ
description: Frequently asked questions about the documentation engine
order: 3
---

# Frequently Asked Questions

Find answers to common questions about using the documentation engine.

## General

### How do I add a new page?

Simply create a new `.md` file in the `src/content/docs/` directory. The file will automatically appear in the sidebar navigation.

```
src/content/docs/
└── my-new-page.md   # Creates /docs/my-new-page
```

### How do I create a new section?

Create a new folder with an `index.md` file:

```
src/content/docs/
└── my-section/
    ├── index.md     # Section overview
    ├── page-one.md
    └── page-two.md
```

### How do I control page order?

Use the `order` frontmatter property:

```markdown
---
title: My Page
order: 1
---
```

Lower numbers appear first in the sidebar.

## Frontmatter

### What frontmatter properties are available?

| Property | Type | Description |
|----------|------|-------------|
| `title` | string | Page title (required) |
| `description` | string | Page description for SEO |
| `order` | number | Sort order in sidebar |

### Example frontmatter

```markdown
---
title: Getting Started
description: Learn how to get started with our product
order: 1
---

# Getting Started

Your content here...
```

## Styling

### How do I customize the theme colors?

Edit the `tailwind.config.cjs` file:

```js
colors: {
  'docs-accent': '#6366f1',      // Primary accent color
  'docs-bg': '#ffffff',           // Light mode background
  'docs-bg-dark': '#0f172a',      // Dark mode background
}
```

### Can I use custom CSS?

Yes! Add your styles to `src/styles/global.css`. Use Tailwind's `@layer` directive to organize your styles:

```css
@layer components {
  .my-custom-class {
    @apply text-blue-500 font-bold;
  }
}
```

## Deployment

### Where can I deploy?

This static site works with any static hosting provider:

- **Cloudflare Pages** (recommended)
- **Netlify**
- **Vercel**
- **GitHub Pages**
- **AWS S3 + CloudFront**

### How do I deploy to Cloudflare Pages?

1. Push your code to GitHub
2. Connect your repository to Cloudflare Pages
3. Set the build command to `npm run build`
4. Set the output directory to `dist`

## Troubleshooting

### My changes aren't showing up

1. Make sure you saved the file
2. Check that the development server is running
3. Hard refresh the browser (Ctrl+Shift+R)

### The sidebar order is wrong

Add `order` frontmatter to your markdown files. Pages without an order value default to 999.

### Dark mode isn't working

Check that:
1. JavaScript is enabled in your browser
2. The theme toggle button is in the navbar
3. LocalStorage isn't blocked

## Still have questions?

Open an issue on GitHub and we'll be happy to help!
