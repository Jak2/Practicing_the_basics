# Blog — Markdown Documentation Engine: Project Report

> **Project:** `my_learning_projects/Blog`
> **Type:** Learning project — Static site generator / documentation engine
> **Date:** 2026-06-23

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Motivation & Learning Goals](#2-motivation--learning-goals)
3. [Tech Stack](#3-tech-stack)
4. [System Architecture & Data Flows](#4-system-architecture--data-flows)
5. [Key Features](#5-key-features)
6. [Component Deep Dives](#6-component-deep-dives)
7. [Challenges & Solutions](#7-challenges--solutions)
8. [Project Structure](#8-project-structure)
9. [Known Limitations & Future Improvements](#9-known-limitations--future-improvements)
10. [What Was Learned](#10-what-was-learned)

---

## 1. Executive Summary

The Markdown Documentation Engine (project name: Blog) is a static documentation site that turns a folder of Markdown files into a fully-featured docs website — with auto-generated sidebar navigation, client-side search, a Table of Contents, dark mode, and responsive layout — without any backend server or database.

The content model is intentionally simple: drop a `.md` file into `src/content/docs/`, and it automatically appears in the sidebar and becomes a navigable page. Folder structure becomes URL structure. Frontmatter controls title, SEO description, and sort order.

What makes it distinct is the **zero-runtime-server** philosophy: Astro compiles everything at build time into static HTML files. The resulting `dist/` folder can be hosted on any CDN (Cloudflare Pages, GitHub Pages, Netlify, Vercel) with no server required. All interactive features — search, dark mode, mobile sidebar, scroll-spy TOC — run entirely in the browser as small vanilla JavaScript scripts.

---

## 2. Motivation & Learning Goals

### The Problem

Most documentation sites either require a complex CMS backend (WordPress, Contentful) or are tightly coupled to a specific tool (GitBook, Notion). The goal was to build something that:

- Has **no backend** — just HTML, CSS, and minimal JS
- Lets content authors write in **Markdown** without touching code
- Generates **navigation automatically** from the file system
- Is **fast to deploy** anywhere as static files

### Learning Goals

| Goal | How It Was Explored |
|------|---------------------|
| Astro static site generation | Built the entire site on Astro 3.5; learned build lifecycle, component model |
| `import.meta.glob()` | Used for both sidebar tree building and search index generation at build time |
| File-based routing with dynamic catch-all routes | `pages/docs/[...slug].astro` with `getStaticPaths()` |
| Build-time data fetching | All markdown discovery happens at build — no runtime API calls |
| Tailwind CSS | Used throughout; learned `dark:` variants, typography plugin, custom tokens |
| Client-side search | Built from scratch — weighted scoring, debouncing, match highlighting |
| IntersectionObserver API | Used for TOC scroll spy to highlight the active heading as you scroll |
| Component slots (Astro) | Named slots (`slot="toc"`) to inject the TOC into the right sidebar |
| Static site deployment | Zero-dependency deployment to any CDN |

---

## 3. Tech Stack

| Technology | Version | Role |
|------------|---------|------|
| **Astro** | 3.5+ | Static site generator — routing, build pipeline, component model |
| **@astrojs/tailwind** | 5.0+ | Official Astro integration for Tailwind CSS |
| **Tailwind CSS** | 3.3+ | Utility-first CSS, dark mode (`class` strategy), responsive breakpoints |
| **@tailwindcss/typography** | 0.5+ | `prose` class for beautiful Markdown-rendered content |
| **PostCSS + Autoprefixer** | — | Processes Tailwind CSS directives |
| **Vanilla JavaScript** | ES2020 | Dark mode, search engine, mobile menu, TOC scroll spy |
| **IntersectionObserver API** | Browser built-in | Scroll spy for active heading detection |
| **localStorage** | Browser built-in | Persisting dark mode preference across sessions |
| **import.meta.glob()** | Vite built-in | Build-time file discovery — loads all `.md` files at once |

**No backend. No database. No runtime server.**

---

## 4. System Architecture & Data Flows

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER REQUEST                            │
│               e.g., /docs/getting-started/install           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     ASTRO ROUTER                             │
│          pages/docs/[...slug].astro (catch-all)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     LAYOUT SYSTEM                            │
│                  layouts/BaseLayout.astro                    │
│   ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌─────────┐  │
│   │  Navbar  │  │ Sidebar  │  │  Content   │  │   TOC   │  │
│   │(search+  │  │ (auto-   │  │  (Markdown │  │ (scroll │  │
│   │  theme)  │  │  built)  │  │  rendered) │  │   spy)  │  │
│   └──────────┘  └──────────┘  └────────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    RENDERED STATIC HTML                      │
│           Served to browser — no server required             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Build-Time Flow

Everything that matters happens at build time (`npm run build`):

```
Developer edits src/content/docs/**/*.md
              │
              ▼
    import.meta.glob() discovers all .md files
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
Sidebar builds        Search index built
tree from paths       (titles + headings + excerpts)
    │                    │
    ▼                    │
Navigation HTML         │
emitted into layout      │
                         ▼
              Markdown → Astro components
              → getStaticPaths() generates all routes
              → Pages rendered into HTML
              → Search JSON embedded in <script> tag
              │
              ▼
         dist/ (static files)
              │
              ▼
         Deploy to CDN / GitHub Pages
```

### 4.3 Request Flow (URL → Rendered Page)

```
URL: /docs/getting-started/install
              │
              ▼
  [... slug] = "getting-started/install"
              │
              ▼
  getStaticPaths() has pre-generated this route
              │
              ▼
  import.meta.glob finds:
  /src/content/docs/getting-started/install.md
              │
              ▼
  Extract: frontmatter (title, description)
           getHeadings() → TOC array
           prev/next pages by index
              │
              ▼
  BaseLayout wraps content:
  Sidebar (left) + Content (center) + TOC (right)
              │
              ▼
  Static HTML sent to browser
  Client JS hydrates: dark mode, search, scroll spy
```

### 4.4 Runtime Flow (Client-Side)

After the static HTML loads, three independent JS scripts activate:

| Script | Trigger | Action |
|--------|---------|--------|
| **Dark mode init** | Page load | Reads `localStorage` → applies `dark` class to `<html>` before first paint |
| **Theme toggle** | Button click | Toggles `dark` class → saves to `localStorage` |
| **Search engine** | User types (debounced 150ms) | Parses embedded JSON index → scores results → renders dropdown |
| **Mobile menu** | Hamburger click | Clones sidebar HTML into overlay panel → slide-in animation |
| **TOC scroll spy** | User scrolls | `IntersectionObserver` detects visible heading → highlights TOC link |

### 4.5 Component Communication

```
              src/content/docs/**/*.md
                        │
         ┌──────────────┼─────────────────┐
         │              │                 │
         ▼              ▼                 ▼
   Sidebar.astro   [...slug].astro   Navbar.astro
   (tree builder)  (page renderer)   (search index)
         │              │                 │
         │  navigation  │  content +      │  search JSON
         │  HTML        │  headings[]     │  embedded
         └──────────────┼─────────────────┘
                        │
                        ▼
               BaseLayout.astro
               (assembles slots)
                        │
                        ▼
                Static HTML Output
```

---

## 5. Key Features

### 5.1 Filesystem-Based Routing & Auto-Generated Sidebar

The most important design choice: **your folder structure is your navigation**. No config files, no manual sidebar definitions.

```
src/content/docs/
├── getting-started/
│   ├── index.md        →  /docs/getting-started    (section landing)
│   ├── install.md      →  /docs/getting-started/install
│   └── faq.md          →  /docs/getting-started/faq
└── guides/
    ├── index.md        →  /docs/guides
    └── advanced.md     →  /docs/guides/advanced
```

`Sidebar.astro` runs at build time, calls `import.meta.glob('/src/content/docs/**/*.md')`, converts file paths to routes, then builds a nested tree that becomes the collapsible navigation. Sections with children render as `<details>` elements (native collapsible, no JS required). The currently active section auto-expands.

### 5.2 Client-Side Search (Ctrl+K)

A full search engine built without any external library:

- **Build-time**: `Navbar.astro` reads all markdown modules via `import.meta.glob()`, extracts page titles, headings, and 200-character content excerpts. This forms a `SearchEntry[]` array serialised into a `<script type="application/json">` tag in the page HTML.
- **Runtime**: On user input (debounced 150ms), the JS reads the embedded JSON, splits the query into terms, scores each page:
  - Title match: +10 per term
  - Heading match: +5 per term
  - Content excerpt match: +2 per term
- Top 8 results shown in a dropdown with match highlighting (`<mark>` tags, yellow background).
- Keyboard shortcut: `Ctrl+K` / `Cmd+K` to focus, `Escape` to close.

### 5.3 Table of Contents with Scroll Spy

The right sidebar (`TableOfContents.astro`) receives a `headings[]` prop from the parent page (extracted via Astro's `getHeadings()` function on the markdown module). It renders h1–h3 headings with indentation by depth.

Scroll spy uses the `IntersectionObserver` API with `rootMargin: '-80px 0px -80% 0px'` — this triggers when a heading enters the top 20% of the viewport (adjusted for the 64px fixed navbar). When an entry intersects, the matching TOC link gains the active highlight class.

The page title from frontmatter is prepended to the headings array as a synthetic h1, so it always appears as the first TOC entry.

### 5.4 Dark Mode

Uses Tailwind's class-based dark mode strategy (`darkMode: 'class'`). A small script in `BaseLayout.astro` runs synchronously before the page renders (preventing a flash of wrong theme):

```javascript
const stored = localStorage.getItem('theme');
if (stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark');
}
```

The toggle button in the Navbar flips the `dark` class and saves the choice to `localStorage`. Tailwind's `dark:` variants handle all color switching across components.

### 5.5 Responsive 3-Column Layout

| Breakpoint | Layout |
|------------|--------|
| Mobile (< lg / 1024px) | Single column; hamburger menu opens sidebar overlay |
| Large (lg+) | Left sidebar visible + main content |
| Extra Large (xl+, 1280px) | Left sidebar + main content + right TOC |

The mobile sidebar overlay clones the desktop sidebar HTML via `sidebar.innerHTML` and animates it in as a slide-in panel with a blurred backdrop. Body scroll is locked while open (`document.body.style.overflow = 'hidden'`).

### 5.6 Previous / Next Page Navigation

At the bottom of every page, links to adjacent docs pages are generated in `[...slug].astro`. The full page list is built from `import.meta.glob()`, then the current page's index is found. `pageList[currentIndex - 1]` and `pageList[currentIndex + 1]` become the prev/next links, using frontmatter title if available or a filename-derived title as fallback.

### 5.7 Frontmatter Control

Each markdown file can include a YAML frontmatter block:

```yaml
---
title: Getting Started        # Sidebar label + page <h1>
description: Learn how to...  # SEO meta description
order: 1                       # Sidebar sort order (lower = first)
---
```

The `order` field is read by `Sidebar.astro` to sort pages within their section (default: 999, so unlabeled pages sort last).

### 5.8 Custom Prose Styles & Callout Boxes

`global.css` defines Tailwind component classes for styled callouts:

| Class | Appearance | Use Case |
|-------|-----------|----------|
| `.callout-info` | Blue left border | Notes and tips |
| `.callout-warning` | Amber left border | Caution notices |
| `.callout-error` | Red left border | Error conditions |
| `.callout-success` | Green left border | Completion confirmations |

Inline code renders with a pink highlight; code blocks have a dark background with syntax highlighting; tables have border styling. All handled via `@layer components` in `global.css`.

---

## 6. Component Deep Dives

### 6.1 Sidebar.astro — Tree Building Algorithm

The sidebar builds navigation from a flat file list in 4 steps:

**Step 1 — Scan files:**
```javascript
const mods = import.meta.glob('/src/content/docs/**/*.md', { eager: true });
```

**Step 2 — Convert paths to page metadata:**
```javascript
// /src/content/docs/getting-started/install.md
// → { route: '/docs/getting-started/install', title: 'Install', order: 999 }
fileToRoute(filePath):
  remove /src/content/docs prefix
  remove .md suffix
  collapse /index → parent route
```

**Step 3 — Build nested tree (`buildTree()`):**
Splits each route into path segments and walks the tree, creating nodes as needed:
```javascript
// /docs/getting-started/install
// segments: ['getting-started', 'install']
// Creates: root.children['getting-started'].children['install'].__meta = pageData
```

**Step 4 — Render as HTML:**
- Nodes with children → `<details open={hasActiveChild}>` with `<summary>`
- Leaf nodes → `<a>` links
- Active page gets indigo accent + background highlight
- `isActive()` compares `Astro.url.pathname` to route; `hasActiveChild()` walks descendants

### 6.2 Navbar.astro — Search Engine

The search system is built in two phases:

**Build phase** — `Navbar.astro` server-side script:
- Reads all markdown modules via `import.meta.glob()`
- Extracts: title (from frontmatter or filename), headings array (from `getHeadings()`), text excerpt (200 chars from `rawContent()` with HTML/markdown stripped)
- Serialises `SearchEntry[]` to JSON → embedded as `<script type="application/json" id="search-data">`

**Runtime phase** — client script in `<script>` tag:
- On page load, reads the embedded JSON: `JSON.parse(document.getElementById('search-data').textContent)`
- On input (debounced 150ms): splits query into terms, scores all entries, filters `score > 0`, sorts descending, slices top 8
- Renders dropdown with `highlightMatch()` — uses regex to wrap matching substrings in `<mark>` tags
- `escapeHtml()` prevents XSS before inserting matched text into innerHTML

### 6.3 TableOfContents.astro — IntersectionObserver Scroll Spy

Receives `headings: Array<{depth, slug, text}>` as a prop. Renders `h1–h3` as indented links. Client JS:

```javascript
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // Find matching TOC link by href="#slug"
        // Add active classes, remove from all others
      }
    });
  },
  { rootMargin: '-80px 0px -80% 0px', threshold: 0 }
);

document.querySelectorAll('.docs-content h1, .docs-content h2, .docs-content h3')
  .forEach((h) => observer.observe(h));
```

The `rootMargin` top offset (`-80px`) accounts for the sticky navbar height. The bottom offset (`-80%`) means only headings in the top 20% of the viewport trigger the highlight — so the active heading is always the one you're currently reading, not one far below.

### 6.4 `[...slug].astro` — Dynamic Catch-All Route

The `[...slug]` syntax captures any path under `/docs/*`. Because Astro is a static site generator, all valid paths must be declared at build time:

```javascript
export function getStaticPaths() {
  const modules = import.meta.glob('/src/content/docs/**/*.md', { eager: true });
  return Object.keys(modules).map((filePath) => {
    // Convert file path → slug string
    const slugPath = route.replace(/^\/docs\/?/, '');
    return { params: { slug: slugPath || undefined } };
    // undefined slug → /docs (the root docs page)
  });
}
```

At render time, `Astro.params.slug` is used to look up the matching markdown module, extract its content and headings, compute prev/next pages, and render everything inside `BaseLayout`.

Named slot usage:
```astro
<BaseLayout>
  <article>  <!-- fills default <slot /> --></article>
  <TableOfContents slot="toc" headings={headings} />  <!-- fills <slot name="toc" /> -->
</BaseLayout>
```

---

## 7. Challenges & Solutions

### Bug 1: `getStaticPaths()` Error

**Problem:** The `[...slug].astro` dynamic route threw a build error because `getStaticPaths()` was missing. Astro requires all dynamic routes to declare their valid paths at build time for static generation.

**Root cause:** Rest params (`[...slug]`) in Astro's SSG mode cannot be resolved without an explicit path manifest.

**Fix:** Added `getStaticPaths()` that runs `import.meta.glob()` over all markdown files and returns the full list of `{ params: { slug } }` objects — one per markdown file.

---

### Bug 2: Invalid Route Parameter (Array vs String)

**Problem:** After adding `getStaticPaths()`, routes with nested paths (e.g., `getting-started/install`) failed because the slug was being passed as an array `['getting-started', 'install']` instead of a string.

**Root cause:** Misunderstanding of Astro rest params behaviour — `[...slug]` captures a single string (the full remaining path), not an array of segments.

**Fix:** Changed slug handling to treat it as a plain string path and use string operations (`.replace()`, `.split()`) rather than array operations.

---

### Bug 3: Headings Hidden Behind Fixed Navbar

**Problem:** Clicking a TOC link jumped to a heading, but the heading landed directly behind the 64px sticky navbar — making it appear as if nothing happened.

**Root cause:** CSS anchor links scroll to the element's top edge with no offset for fixed headers.

**Fix:** Added two CSS properties:
```css
:root { --navbar-height: 4rem; }

/* scrolling via links */
html { scroll-padding-top: var(--navbar-height); }

/* scrolling via TOC/search links */
[id] { scroll-margin-top: var(--navbar-height); }
```
`scroll-padding-top` adjusts where the browser considers the "top" of the scrollport when scrolling to an anchor. `scroll-margin-top` applies the same offset to the element itself.

---

### Design Decision 1: Build-Time Search Index

Client-side search could have been done entirely at runtime (fetching a JSON index from a static file). Instead, the search index is embedded directly into the HTML of every page as a `<script type="application/json">` tag. This means:
- No extra network request for the index
- Search works even without a separate API or fetch
- The index is always in sync with the page (built at the same time)

Trade-off: every page carries the full search index in its HTML. For a large docs site, this would add overhead. Acceptable for a learning project with < 50 pages.

---

### Design Decision 2: No External Search Library

The search engine is ~80 lines of vanilla JS. The alternative — Lunr.js, FlexSearch, Fuse.js — would have added a dependency and more complexity. The custom implementation demonstrates the core concepts (term splitting, weighted scoring, result highlighting) with no abstraction overhead.

---

### Design Decision 3: Sidebar via `<details>` Native Collapsible

Collapsible sidebar sections use the HTML `<details>`/`<summary>` elements with `open={hasActiveChild}` for auto-expansion. No JavaScript needed for the accordion behaviour. The `details summary::-webkit-details-marker { display: none }` CSS rule hides the browser's default triangle marker so a custom SVG chevron can be used.

---

### Design Decision 4: Mobile Sidebar via DOM Cloning

Rather than maintaining a separate mobile navigation component, the mobile overlay clones the desktop sidebar's HTML via `sidebar.innerHTML`. This ensures the mobile and desktop navs are always in sync without a shared state management layer or a duplicated template.

---

## 8. Project Structure

```
Blog/
├── src/
│   ├── components/
│   │   ├── Navbar.astro          # Sticky header: search + dark mode + mobile menu
│   │   ├── Sidebar.astro         # Auto-built left nav from markdown file tree
│   │   └── TableOfContents.astro # Right sidebar TOC with IntersectionObserver
│   │
│   ├── content/
│   │   └── docs/                 # ALL markdown content lives here
│   │       ├── getting-started/
│   │       │   ├── index.md      # /docs/getting-started (section landing)
│   │       │   ├── install.md    # /docs/getting-started/install
│   │       │   └── faq.md        # /docs/getting-started/faq
│   │       ├── guides/
│   │       │   ├── index.md      # /docs/guides
│   │       │   └── advanced.md   # /docs/guides/advanced
│   │       └── ai/               # Example custom sections
│   │           ├── ai.md
│   │           └── agent.md
│   │
│   ├── layouts/
│   │   └── BaseLayout.astro      # Master template: head, navbar, 3-column grid, slots
│   │
│   ├── pages/
│   │   ├── index.astro           # Home page (/)
│   │   └── docs/
│   │       └── [...slug].astro   # Catch-all for /docs/* — routing + rendering
│   │
│   ├── styles/
│   │   └── global.css            # Tailwind directives + custom prose + callout classes
│   │
│   └── env.d.ts                  # TypeScript types for Astro
│
├── public/
│   └── favicon.svg               # Site favicon
│
├── dist/                         # Build output (gitignored) — deploy this
│
├── astro.config.mjs              # Astro config (site URL, Tailwind integration)
├── tailwind.config.cjs           # Custom color tokens, fonts, dark mode strategy
├── postcss.config.cjs            # PostCSS plugins for Tailwind
├── package.json                  # Dependencies (astro, @astrojs/tailwind, tailwindcss)
├── README.md                     # Features, quick start, customization guide
├── ARCHITECTURE.md               # Internal architecture: request flow, component details
├── PROJECT_JOURNEY.md            # Setup guide, tech context, cross-platform packaging
└── CHANGELOG.md                  # Feature additions and bug fixes history
```

---

## 9. Known Limitations & Future Improvements

### Current Limitations

| Limitation | Detail |
|------------|--------|
| Shallow search index | Search uses only 200-char excerpts; long pages may not surface relevant content buried deep in the page |
| No authentication | Entirely public static site — no per-page access control |
| Sidebar only 2 levels deep | The tree renderer supports sections and their direct children; deeper nesting (3+ levels) is not rendered |
| Tailwind CDN comment in docs | `PROJECT_JOURNEY.md` mentions CDN Tailwind but the actual project uses local Tailwind build via `@astrojs/tailwind` — minor inconsistency in documentation |
| Search index in every page | Full search JSON is embedded in every page's HTML — grows linearly with doc count |
| No build-time image optimisation | Images in markdown are not run through Astro's image optimisation pipeline |

### Planned Improvements (from PROJECT_JOURNEY.md)

1. **Full frontmatter `order` support and sorting** — currently implemented; was a listed next step at time of writing
2. **Active-route highlighting in sidebar** — now implemented via `isActive()` / `hasActiveChild()`
3. **Accessible off-canvas mobile menu** — replace the DOM-clone overlay with a proper `<dialog>` or ARIA-compliant component
4. **Deeper sidebar nesting** — extend `buildTree()` to render 3+ level deep structures
5. **Per-page search** — add in-page `Ctrl+F`-style filtering as complement to global search
6. **Cross-platform packaging** — Capacitor wrapper for Android/iOS; Tauri for Windows desktop app
7. **CI/CD pipeline** — GitHub Actions workflow to build and deploy to Cloudflare Pages on push
8. **Search index chunking** — Move search index to a separately loaded JSON file to reduce per-page HTML size for large doc sets

---

## 10. What Was Learned

### 1. Astro's Build-Time Mindset

Astro encourages thinking in two distinct phases: **build time** (where all file I/O and data fetching happens) and **runtime** (where only small client scripts run). This mental model leads to fast, dependency-free pages. The key insight: anything you can do at build time, you should — it costs nothing at runtime.

### 2. `import.meta.glob()` as a Build-Time Filesystem API

`import.meta.glob('/src/content/docs/**/*.md', { eager: true })` is Vite's mechanism for importing many files at once. It returns a map of file path → module object at build time. This is how both the sidebar and search index work — they read the filesystem, not an API. The pattern is reusable anywhere content needs to be discovered dynamically from files.

### 3. `getStaticPaths()` is Required for Dynamic Routes in SSG

Any route with a dynamic segment (`[slug]`, `[...slug]`) in a static site generator must declare all valid paths ahead of time. Astro enforces this via `getStaticPaths()`. The function runs once at build time and returns an array of param objects — each becomes a pre-rendered HTML file in `dist/`.

### 4. IntersectionObserver for Scroll Interactions

`IntersectionObserver` is the correct API for detecting which element is currently visible on screen. It is more performant than scroll event listeners because it fires only when visibility changes, not on every scroll tick. The `rootMargin` property allows fine-tuning of the detection zone — negative values shrink the viewport area that triggers intersection.

### 5. Tailwind Dark Mode with Class Strategy

Tailwind's `class` dark mode strategy (as opposed to `media`) means dark mode is toggled programmatically by adding/removing a `dark` class on `<html>`. This enables user-controlled overrides on top of system preferences. The pattern: read system preference on first load, but let user choice (stored in `localStorage`) win on subsequent visits.

### 6. CSS Scroll Offset for Fixed Headers

`scroll-padding-top` (on `<html>`) and `scroll-margin-top` (on anchor targets) are the CSS-native solution to the "fixed header hides jump targets" problem. Setting both to the navbar height (`4rem`) via a CSS custom property ensures that anchor navigation, TOC clicks, and search result navigation all land with the heading clearly visible below the sticky bar.

### 7. Astro Named Slots for Composable Layouts

Astro's slot system allows a layout to define multiple named insertion points. The `BaseLayout` defines `<slot />` (main content) and `<slot name="toc" />` (right sidebar). Pages can then inject a `<TableOfContents>` component into the right sidebar without the layout needing to know anything about its implementation. This is the Astro equivalent of component children patterns in React.

### 8. Static Sites for Structured Content

Building this project demonstrated that a backend is often unnecessary for documentation. When content is structured (folders, files, frontmatter) and read-only, a static site generator handles everything. The resulting site is faster, cheaper to host, requires no authentication infrastructure, and has no server-side attack surface.

---

*Project report generated 2026-06-23. Source: `my_learning_projects/Blog`.*
