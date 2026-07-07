---
title: Installation
description: How to install and set up the documentation engine
order: 2
---

# Installation

This guide will walk you through setting up the documentation engine from scratch.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Node.js** - Version 18.14.1 or higher
- **npm** - Usually comes with Node.js

## Installation Steps

### 1. Clone or Download

```bash
# Clone the repository
git clone https://github.com/your-username/docs-engine.git

# Or download and extract the ZIP file
```

### 2. Install Dependencies

Navigate to the project directory and install the required packages:

```bash
cd docs-engine
npm install
```

### 3. Start Development Server

Run the development server to preview your documentation:

```bash
npm run dev
```

Your documentation site will be available at `http://localhost:4321`.

## Building for Production

When you're ready to deploy, build your site:

```bash
npm run build
```

This creates an optimized static site in the `dist/` directory.

### Preview the Build

You can preview the production build locally:

```bash
npm run preview
```

## Configuration

### Site URL

Update the `astro.config.mjs` file with your production URL:

```js
export default defineConfig({
  site: 'https://your-domain.com',
  integrations: [tailwind()],
});
```

### Customizing Colors

Edit `tailwind.config.cjs` to customize the color scheme:

```js
theme: {
  extend: {
    colors: {
      'docs-accent': '#your-color',
    },
  },
}
```

## Troubleshooting

### Port Already in Use

If port 4321 is busy, Astro will automatically try the next available port.

### Build Errors

Make sure all dependencies are installed:

```bash
rm -rf node_modules
npm install
```

## Next Steps

- Learn about [Markdown frontmatter](/docs/getting-started/faq)
- Explore [advanced customization](/docs/guides)
