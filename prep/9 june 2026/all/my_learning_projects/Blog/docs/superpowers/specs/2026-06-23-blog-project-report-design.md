# Design Spec: Blog (Markdown Docs Engine) Project Report

**Date**: 2026-06-23
**Type**: Documentation — Project Report
**Output file**: `BLOG_PROJECT_REPORT.md` (project root)

---

## Purpose

Produce a comprehensive project report for the Markdown Docs Engine (Blog) that answers:
- **What** is this project?
- **Why** was it built?
- **How** was it built (architecture, stack, design decisions)?

Audience: mixed — technical (developers, reviewers) and semi-technical (portfolio readers, interviewers).

---

## Report Structure

### 1. Executive Summary
One-paragraph plain-English summary. What the Markdown Docs Engine is, what problem it solves, what makes it distinct (zero-backend, filesystem-driven, static-first).

### 2. Motivation & Learning Goals
- Problem being solved: lack of a simple, write-once docs site that doesn't require a backend
- Learning goals: Astro SSG, file-based routing, build-time data fetching, Tailwind CSS, client-side search, IntersectionObserver API
- Context: personal learning project under `my_learning_projects/`

### 3. Tech Stack
Table of all technologies with their role in the system.

### 4. System Architecture & Data Flows
- Build-time flow (markdown → sidebar tree → static HTML)
- Runtime flow (dark mode, search, TOC scroll spy, mobile menu)
- Request flow (URL → catch-all route → markdown module → layout)
- Component communication diagram

### 5. Key Features
- Filesystem-based routing & auto-generated sidebar
- Client-side search (Ctrl+K, build-time index, weighted scoring)
- Table of Contents with IntersectionObserver scroll spy
- Dark mode (class-based, localStorage + system preference)
- Responsive 3-column layout with mobile hamburger menu
- Previous/Next page navigation
- Frontmatter support (title, description, order)
- Callout boxes (info, warning, error, success)

### 6. Component Deep Dives
- `Sidebar.astro` — tree building algorithm from flat file list
- `Navbar.astro` — search engine, dark mode, mobile overlay
- `TableOfContents.astro` — IntersectionObserver scroll spy
- `[...slug].astro` — catch-all route, getStaticPaths, prev/next

### 7. Challenges & Solutions
Document the 3 bugs fixed (from CHANGELOG) and key design decisions made.

### 8. Project Structure
Annotated directory tree.

### 9. Known Limitations & Future Improvements
Be honest about what is missing (no full-text search indexing at depth, no auth, no comments, Tailwind CDN vs local build).

### 10. What Was Learned
Key Astro/SSG concepts demonstrated through building this project.

---

## Tone & Style
- Factual, direct — no filler
- Technical terms used but briefly explained
- Code snippets only where they clarify a concept
- Diagrams reproduced from existing docs (ASCII)

---

## Source Files Used
- `README.md` — feature list, quick start, project structure
- `ARCHITECTURE.md` — component responsibilities, data flows, key concepts
- `PROJECT_JOURNEY.md` — tech stack context, packaging notes, next steps
- `CHANGELOG.md` — feature additions, bugs fixed
- `src/pages/docs/[...slug].astro` — routing logic, getStaticPaths, prev/next nav
- `src/components/Sidebar.astro` — tree building algorithm
- `src/components/Navbar.astro` — search engine, dark mode, mobile menu
- `src/components/TableOfContents.astro` — scroll spy
- `astro.config.mjs` + `package.json` — dependency versions
