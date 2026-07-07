---
title: Introduction
description: Get started with the Markdown documentation engine
order: 1
---

# Introduction

Welcome to the documentation engine! This is a modern, Markdown-driven documentation system built with Astro and Tailwind CSS.

## Key Features

- **Filesystem-based routing** - Your folder structure becomes your navigation
- **Markdown first** - Write content in Markdown, no code required
- **Dark mode** - Built-in theme switching with system preference detection
- **Responsive design** - Works beautifully on all devices
- **Fast & static** - Zero JavaScript by default, lightning-fast page loads

## Quick Start

1. Clone the repository
2. Install dependencies with `npm install`
3. Run the development server with `npm run dev`
4. Start adding Markdown files to `src/content/docs/`

## Project Structure

```
src/
├── content/
│   └── docs/           # Your markdown files go here
│       ├── getting-started/
│       │   ├── index.md
│       │   └── install.md
│       └── guides/
│           └── index.md
├── components/
│   ├── Navbar.astro
│   └── Sidebar.astro
├── layouts/
│   └── BaseLayout.astro
└── pages/
    ├── index.astro
    └── docs/
        └── [...slug].astro
```

## Next Steps

- Read the [Installation guide](/docs/getting-started/install) to set up your project
- Check out the [FAQ](/docs/getting-started/faq) for common questions
- Explore the [Guides](/docs/guides) for advanced topics
