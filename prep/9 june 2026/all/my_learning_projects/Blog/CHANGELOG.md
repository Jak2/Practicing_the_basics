# Changelog

All notable changes to this project are documented in this file.

---

## [Unreleased]

### Added
- **Client-side search** — Search bar in the center of the top navbar
  - Build-time search index generated from all markdown files (titles, headings, content excerpts)
  - Weighted scoring: title matches (10), heading matches (5), content matches (2)
  - Keyboard shortcut: `Ctrl+K` / `Cmd+K` to focus, `Escape` to close
  - Debounced input (150ms), max 8 results with match highlighting
  - Dropdown shows page title, matched heading, and content excerpt
- **Table of Contents (right sidebar)** — Displays h1, h2, h3 headings for the current page
  - Scroll spy via IntersectionObserver highlights the active heading
  - Indented hierarchy (h1 flush, h2 indented, h3 more indented)
  - Page title from frontmatter included as first TOC entry
- **Scroll-to-target offset** — CSS variable `--navbar-height` applied via `scroll-margin-top` on all `[id]` elements so headings land below the fixed navbar
- **Previous/Next page navigation** — Bottom-of-page links to adjacent docs pages
- **Font size scaling** — Global base font increased by 2% (`html { font-size: 102% }`); both sidebars receive an additional 2% bump (`font-size: 1.02em`)

### Changed
- **Navbar** — Now a 3-section layout: logo (left), search bar (center), actions (right)
- **Sidebar header** — "Blog" link points to home page (`/`) instead of `/docs`
- **`[...slug].astro`** — Prepends frontmatter title as an h1 heading to the headings array for TOC display

### Fixed
- **`getStaticPaths()` error** — Added required static path generation for the dynamic `[...slug]` route
- **Invalid route parameter** — Changed slug from array to string for Astro rest params
- **Headings hidden behind navbar** — Added `scroll-padding-top` and `scroll-margin-top` using CSS variable

---

## [0.1.0] — Initial Release

### Added
- Astro static site generator with Tailwind CSS integration
- Filesystem-based routing (`src/content/docs/` maps to `/docs/*`)
- Dynamic catch-all route (`pages/docs/[...slug].astro`) with `getStaticPaths()`
- 3-column responsive layout (left sidebar, main content, right TOC)
- Left sidebar auto-generated from markdown file tree with collapsible sections
- Dark mode toggle with localStorage persistence and system preference detection
- Mobile responsive design with hamburger menu and slide-in sidebar overlay
- Markdown rendering with custom prose styles (headings, code blocks, tables, callouts)
- Custom Tailwind theme with docs-specific color tokens
- Inter + JetBrains Mono font loading
- Home page with hero section
