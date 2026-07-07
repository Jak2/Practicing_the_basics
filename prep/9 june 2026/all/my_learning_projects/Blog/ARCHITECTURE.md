# Architecture Guide

This document explains how the documentation engine works internally — the request flow, file responsibilities, and how components communicate with each other.

---

## Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [Request Flow](#request-flow)
3. [File Responsibilities](#file-responsibilities)
4. [Component Communication](#component-communication)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Key Concepts](#key-concepts)

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                              │
│                     (e.g., /docs/guides)                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ASTRO ROUTER                                │
│         pages/docs/[...slug].astro (catch-all route)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LAYOUT SYSTEM                               │
│                    layouts/BaseLayout.astro                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Navbar  │  │ Sidebar  │  │ Main Content │  │    TOC     │  │
│  │(header)  │  │  (left)  │  │   (center)   │  │  (right)   │  │
│  └──────────┘  └──────────┘  └──────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RENDERED HTML                                │
│              (Served to browser as static page)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow

### Step-by-Step: What happens when you visit `/docs/getting-started/install`

```
1. URL Request
   └── /docs/getting-started/install

2. Astro Router Matches
   └── pages/docs/[...slug].astro
       └── slug = "getting-started/install" (string for rest params)

3. Page Component Executes
   ├── getStaticPaths() generates all valid routes at build time
   ├── import.meta.glob() loads ALL markdown files
   ├── Finds matching file: content/docs/getting-started/install.md
   ├── Extracts frontmatter (title, description)
   └── Extracts headings via getHeadings() for TOC

4. Layout Wraps Content
   └── BaseLayout.astro receives the page
       ├── Navbar.astro (header with dark mode toggle)
       ├── Sidebar.astro (left nav - dynamically built from markdown files)
       ├── <slot /> (receives markdown content as HTML)
       └── <slot name="toc" /> (receives TableOfContents component)

5. Static HTML Generated
   └── Complete page sent to browser
   └── Client-side JS hydrates (dark mode, mobile menu, TOC scroll spy)
```

---

## File Responsibilities

### Configuration Files

| File | Purpose |
|------|---------|
| `astro.config.mjs` | Astro configuration — site URL, integrations (Tailwind) |
| `tailwind.config.cjs` | Tailwind configuration — custom colors, fonts, typography plugin |
| `postcss.config.cjs` | PostCSS plugins — processes Tailwind directives |
| `package.json` | Dependencies and npm scripts |

### Source Files

#### `src/pages/` — Route Definitions

```
pages/
├── index.astro              # Home page (/)
└── docs/
    └── [...slug].astro      # Catch-all for /docs/* routes
```

**`index.astro`** — Landing Page
- Renders the home page at `/`
- Contains hero section, feature cards, CTA buttons
- Uses BaseLayout for consistent structure

**`[...slug].astro`** — Dynamic Documentation Router
- Catches ALL routes under `/docs/*`
- The `[...slug]` syntax means "any path segments"
- **Requires `getStaticPaths()`** for static site generation
- Examples:
  - `/docs` → slug = undefined
  - `/docs/guides` → slug = "guides"
  - `/docs/getting-started/install` → slug = "getting-started/install"

```javascript
// getStaticPaths generates all valid routes at build time
export function getStaticPaths() {
  const modules = import.meta.glob('/src/content/docs/**/*.md', { eager: true });
  return Object.keys(modules).map((filePath) => {
    // Convert file path to slug
    const slugPath = route.replace(/^\/docs\/?/, '');
    return { params: { slug: slugPath || undefined } };
  });
}

// How it resolves markdown files:
const { slug } = Astro.params;  // "getting-started/install"
const route = '/docs/' + slug;  // "/docs/getting-started/install"
// Finds: content/docs/getting-started/install.md
```

---

#### `src/layouts/` — Page Structure

**`BaseLayout.astro`** — The Master Template

```
┌────────────────────────────────────────────────────────────────┐
│                         <head>                                  │
│  - Meta tags, fonts (Inter, JetBrains Mono), favicon           │
│  - Dark mode initialization script (prevents flash)             │
└────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────┐
│                        Navbar                                   │
│  [Logo → /]     [🔍 Search docs... Ctrl K]  [GitHub] [🌙/☀️] [☰] │
└────────────────────────────────────────────────────────────────┘
┌──────────────┬──────────────────────────────┬──────────────────┐
│              │                              │                  │
│   Sidebar    │       Main Content           │  Table of        │
│   (lg+)      │       <slot />               │  Contents        │
│   w-64/72    │       max-w-3xl              │  (xl+)           │
│              │                              │  w-56/64         │
│  Blog (→/)   │  ┌────────────────────┐     │                  │
│              │  │  Article Header    │     │  On this page    │
│  ▼ Section 1 │  │  ────────────────  │     │  - Heading 1     │
│    - Page A  │  │                    │     │    - Sub 1       │
│    - Page B  │  │  Markdown Content  │     │    - Sub 2       │
│  ▼ Section 2 │  │                    │     │  - Heading 2     │
│    - Page C  │  │  ────────────────  │     │                  │
│              │  │  Prev/Next Nav     │     │                  │
│              │  └────────────────────┘     │                  │
└──────────────┴──────────────────────────────┴──────────────────┘
```

**Responsive Breakpoints:**
- Mobile (< lg): No sidebars, hamburger menu for navigation
- Large (lg - 1024px+): Left sidebar visible
- Extra Large (xl - 1280px+): Both sidebars visible

**Key Features:**
- Imports global CSS (`styles/global.css`)
- Renders Navbar and Sidebar components
- Provides `<slot />` for page content
- Provides `<slot name="toc" />` for table of contents
- Dark mode script runs before page renders (prevents flash)
- Sidebar font scaling: both sidebars have `font-size: 1.02em` for 2% larger text

---

#### `src/components/` — Reusable UI Pieces

**`Navbar.astro`** — Site Header

```
Responsibilities:
├── Logo/Site title (links to /)
├── Client-side search bar (center of navbar)
│   ├── Builds search index at build time via import.meta.glob()
│   ├── Indexes: page titles, headings, content excerpts (200 chars)
│   ├── Weighted scoring: title (10), headings (5), content (2)
│   ├── Debounced input (150ms) with max 8 results
│   ├── Match highlighting (yellow) in dropdown results
│   ├── Keyboard shortcut: Ctrl+K / Cmd+K to focus, Escape to close
│   └── Search data embedded as <script type="application/json">
├── GitHub link (external, hidden on small screens)
├── Dark mode toggle
│   ├── Sun icon (visible in dark mode)
│   └── Moon icon (visible in light mode)
├── Mobile menu button (visible < lg breakpoint)
└── Mobile sidebar overlay
    ├── Slide-in panel with animation
    ├── Close button
    ├── Clones sidebar content
    └── Backdrop blur effect
```

**Client-Side JavaScript:**
```javascript
// Theme Management
- Reads localStorage for saved theme
- Falls back to system preference (prefers-color-scheme)
- Toggles 'dark' class on <html>
- Persists choice to localStorage

// Client-Side Search
- Parses build-time JSON search index from embedded <script> tag
- Splits query into terms, scores each page by title/heading/content matches
- Renders dropdown with highlighted matches, matched headings, and excerpts
- Ctrl+K / Cmd+K keyboard shortcut to focus search input
- Closes on Escape key or click outside

// Mobile Menu
- Opens overlay on hamburger click
- Clones sidebar content into mobile panel
- Closes on: X button, backdrop click, Escape key
- Prevents body scroll when open
```

---

**`Sidebar.astro`** — Left Navigation Builder

This component dynamically generates navigation from your markdown files.

```
┌─────────────────────────────────────────────────────────────┐
│                    BUILD PROCESS                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SCAN FILES                                               │
│     import.meta.glob('/src/content/docs/**/*.md')           │
│     └── Returns all .md files with their modules             │
│                                                              │
│  2. EXTRACT METADATA                                         │
│     For each file:                                           │
│     ├── file path: /src/content/docs/guides/install.md      │
│     ├── route: /docs/guides/install                          │
│     ├── title: from frontmatter or filename                  │
│     └── order: from frontmatter (default: 999)               │
│                                                              │
│  3. BUILD TREE                                               │
│     Flat list → Nested tree structure                        │
│     {                                                        │
│       children: {                                            │
│         "getting-started": {                                 │
│           __meta: { title, route },                          │
│           children: {                                        │
│             "install": { __meta: {...} },                    │
│             "faq": { __meta: {...} }                         │
│           }                                                  │
│         }                                                    │
│       }                                                      │
│     }                                                        │
│                                                              │
│  4. RENDER HTML                                              │
│     Tree → <details> with <summary> and <ul>                 │
│     ├── Collapsible sections for folders                     │
│     ├── Links for pages                                      │
│     ├── Active state highlighting (indigo accent)            │
│     └── Auto-expand sections with active children            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Functions:**

```javascript
fileToRoute(filePath)
// "/src/content/docs/guides/install.md" → "/docs/guides/install"
// "/src/content/docs/guides/index.md" → "/docs/guides"

titleFromModule(module, filePath)
// Uses frontmatter.title if available
// Falls back to filename: "install" → "Install"
// Special case: "index" → parent folder name

buildTree(pages)
// Converts flat array of pages into nested tree
// Used for recursive rendering

isActive(route)
// Checks if current URL matches this route
// Used for highlighting active page

hasActiveChild(node)
// Checks if any descendant is active
// Used to auto-expand parent sections
```

**Header Link:**
- "Blog" link at top points to home page (`/`)

---

**`TableOfContents.astro`** — Right Sidebar (Page Headings)

Displays the current page's heading structure for quick navigation.

```
┌─────────────────────────────────────────────────────────────┐
│                    TABLE OF CONTENTS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Props:                                                      │
│  └── headings: Array<{ depth, slug, text }>                 │
│      (extracted from markdown via getHeadings())             │
│                                                              │
│  Filtering:                                                  │
│  └── Shows h1, h2, and h3 headings (depth 1-3)              │
│                                                              │
│  Indentation:                                                │
│  ├── h1: No indent, bold font                               │
│  ├── h2: ml-3 (slight indent)                               │
│  └── h3: ml-6 (more indent)                                 │
│                                                              │
│  Features:                                                   │
│  ├── Clickable links with smooth scroll                     │
│  ├── Active heading highlighting on scroll                  │
│  └── IntersectionObserver for scroll spy                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Client-Side JavaScript (Scroll Spy):**
```javascript
// Highlights the currently visible heading in the TOC
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      // Add highlight to matching TOC link
      // Remove highlight from others
    }
  });
}, {
  rootMargin: '-80px 0px -80% 0px',  // Trigger near top of viewport
});

// Observe all h1, h2, h3 in .docs-content
headings.forEach((heading) => observer.observe(heading));
```

---

#### `src/styles/` — Styling

**`global.css`** — Global Styles

```css
/* Layer 1: Tailwind Base */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* CSS Variables */
:root {
  --navbar-height: 4rem;  // Used for scroll-margin-top offset
}

/* Layer 2: Base Overrides */
@layer base {
  - Global font-size: 102% (2% increase on all rem-based sizes)
  - Smooth scrolling (scroll-behavior: smooth)
  - scroll-padding-top: var(--navbar-height) (accounts for sticky header)
  - scroll-margin-top on all [id] elements (headings land below fixed nav)
  - Focus ring styles (accessibility)
  - Custom scrollbar styling (thin, rounded)
  - Text selection colors (indigo)
}

/* Layer 3: Component Styles */
@layer components {
  .prose h1, h2, h3, h4 { ... }  // Heading styles with borders
  .prose p { ... }                // Paragraph styles
  .prose a { ... }                // Link styles (indigo accent)
  .prose code { ... }             // Inline code (pink highlight)
  .prose pre { ... }              // Code blocks (dark background)
  .prose table { ... }            // Tables with borders
  .callout-info { ... }           // Blue info box
  .callout-warning { ... }        // Amber warning box
  .callout-error { ... }          // Red error box
  .callout-success { ... }        // Green success box
}

/* Layer 4: Utilities */
@layer utilities {
  .transition-theme { ... }       // Color transitions
  .scrollbar-hide { ... }         // Hide scrollbar
}
```

---

#### `src/content/docs/` — Your Content

This is where your markdown files live. The structure directly maps to URLs:

```
content/docs/
├── getting-started/
│   ├── index.md        →  /docs/getting-started
│   ├── install.md      →  /docs/getting-started/install
│   └── faq.md          →  /docs/getting-started/faq
├── guides/
│   ├── index.md        →  /docs/guides
│   └── advanced.md     →  /docs/guides/advanced
└── ai/                  # Example: custom sections
    ├── ai.md           →  /docs/ai/ai
    └── agent.md        →  /docs/ai/agent
```

**Frontmatter Schema:**
```yaml
---
title: Page Title          # Required: shown in sidebar and <h1>
description: SEO text      # Optional: meta description
order: 1                   # Optional: sort order (lower = first)
---
```

---

## Component Communication

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      AT BUILD TIME                               │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  Markdown Files │
                    │  (content/docs) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Sidebar   │      │ [...slug]   │      │     TOC     │
│  Component  │      │    Page     │      │  Component  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │ Navigation         │ Content +          │ Heading
       │ Tree               │ getHeadings()      │ Links
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │   BaseLayout    │
                    │   (combines)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Static HTML    │
                    │    Output       │
                    └─────────────────┘
```

### Runtime Flow (Client-Side)

```
┌─────────────────────────────────────────────────────────────────┐
│                      AT RUNTIME                                  │
└─────────────────────────────────────────────────────────────────┘

    User loads page
          │
          ▼
    ┌─────────────┐
    │  Dark Mode  │  ← Reads localStorage / system preference
    │   Script    │  → Adds 'dark' class to <html> immediately
    └─────────────┘
          │
          ▼
    ┌─────────────┐
    │   Navbar    │  ← User clicks theme toggle
    │   Script    │  → Toggles 'dark' class
    └─────────────┘    → Saves to localStorage
          │
          ├─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │  CSS Rules  │       │  TOC Scroll │       │   Search    │
    │  (Tailwind) │       │    Spy      │       │   Engine    │
    └─────────────┘       └─────────────┘       └─────────────┘
          │                     │                     │
          │ dark: variants      │ Highlights active   │ Parses JSON index
          │ activate            │ heading on scroll   │ Scores & ranks
          ▼                     ▼                     ▼
    Colors change         TOC updates           Results dropdown
```

---

## Key Concepts

### 1. Static Site Generation (SSG)

All pages are pre-rendered at build time:
- No server required at runtime
- Fast page loads (just HTML/CSS/JS)
- Can be hosted on any CDN
- **Requires `getStaticPaths()`** for dynamic routes

### 2. Catch-All Routes with getStaticPaths

The `[...slug]` syntax captures any path, but requires generating all paths at build time:
```javascript
export function getStaticPaths() {
  // Must return all valid { params: { slug } } combinations
  return [
    { params: { slug: undefined } },           // /docs
    { params: { slug: "guides" } },            // /docs/guides
    { params: { slug: "getting-started/faq" }} // /docs/getting-started/faq
  ];
}
```

### 3. import.meta.glob()

Astro's way to import multiple files at once:
```javascript
const mods = import.meta.glob('/src/content/docs/**/*.md', { eager: true });
// Returns: {
//   "/src/content/docs/install.md": {
//     default: Component,
//     frontmatter: {...},
//     getHeadings: () => [...]
//   }
// }
```

### 4. Component Slots

Astro's slot system allows content injection:
```astro
<!-- BaseLayout.astro -->
<main>
  <slot />  <!-- Default slot -->
</main>
<aside>
  <slot name="toc" />  <!-- Named slot -->
</aside>

<!-- Usage in [...slug].astro -->
<BaseLayout>
  <article>Content here</article>
  <TableOfContents slot="toc" headings={headings} />
</BaseLayout>
```

### 5. Dark Mode Strategy

Uses class-based dark mode (`darkMode: 'class'` in Tailwind):
```html
<html class="dark">  <!-- Dark mode active -->
  <body class="bg-white dark:bg-docs-bg-dark">
```

### 6. getHeadings() for TOC

Markdown files expose a `getHeadings()` function:
```javascript
const headings = page.module.getHeadings?.() || [];
// Returns: [
//   { depth: 1, slug: "introduction", text: "Introduction" },
//   { depth: 2, slug: "getting-started", text: "Getting Started" },
//   { depth: 3, slug: "prerequisites", text: "Prerequisites" }
// ]
```

---

## Adding New Features

### Add a New Page

1. Create `src/content/docs/my-page.md`
2. Add frontmatter with title
3. Write content in Markdown
4. Page automatically appears in sidebar

### Add a New Section

1. Create folder: `src/content/docs/my-section/`
2. Add `index.md` with section overview
3. Add additional `.md` files
4. Section appears as collapsible group

### Customize Sidebar Order

Add `order` to frontmatter:
```yaml
---
title: First Page
order: 1
---
```

### Add New Component

1. Create `src/components/MyComponent.astro`
2. Import in layout or page: `import MyComponent from '../components/MyComponent.astro'`
3. Use in template: `<MyComponent />`

---

## Summary

| Concern | File(s) |
|---------|---------|
| Routing | `pages/docs/[...slug].astro` |
| Layout | `layouts/BaseLayout.astro` |
| Left Navigation | `components/Sidebar.astro` |
| Right TOC | `components/TableOfContents.astro` |
| Header/Theme/Search | `components/Navbar.astro` |
| Styling | `styles/global.css` + `tailwind.config.cjs` |
| Content | `content/docs/**/*.md` |
| Config | `astro.config.mjs` |

### Component Visibility by Breakpoint

| Component | Mobile | lg (1024px+) | xl (1280px+) |
|-----------|--------|--------------|--------------|
| Navbar | ✓ | ✓ | ✓ |
| Left Sidebar | Hidden (hamburger menu) | ✓ | ✓ |
| Right TOC | Hidden | Hidden | ✓ |
| Main Content | Full width | With left sidebar | With both sidebars |

The architecture follows a clear separation:
- **Pages** define routes (with `getStaticPaths` for dynamic routes)
- **Layouts** define structure (3-column on large screens)
- **Components** define reusable UI (Navbar, Sidebar, TOC)
- **Content** defines documentation (Markdown files)
- **Styles** define appearance (Tailwind + custom CSS)

Everything comes together at build time to produce fast, static HTML pages.
