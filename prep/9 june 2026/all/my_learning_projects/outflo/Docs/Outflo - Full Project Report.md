# Outflo — Full Project Report

> **Platform:** AI Prompt & Workflow Platform
> **Stack:** Next.js 14 · TypeScript · Tailwind CSS · Markdown · Vercel
> **Status:** MVP Complete — Production-ready, Vercel-deployable

---

## Table of Contents

1. [Project Vision & Problem Statement](#1-project-vision--problem-statement)
2. [Business Context & Goals](#2-business-context--goals)
3. [Tech Stack & Rationale](#3-tech-stack--rationale)
4. [Architecture Design](#4-architecture-design)
5. [Project Structure](#5-project-structure)
6. [Data Model & Content Layer](#6-data-model--content-layer)
7. [Core Feature Deep Dives](#7-core-feature-deep-dives)
8. [UI/UX Design System](#8-uiux-design-system)
9. [SEO Architecture](#9-seo-architecture)
10. [Performance Optimizations](#10-performance-optimizations)
11. [Component Architecture](#11-component-architecture)
12. [Routing & Navigation](#12-routing--navigation)
13. [Dark Mode Implementation](#13-dark-mode-implementation)
14. [Deployment & CI/CD](#14-deployment--cicd)
15. [Scalability Roadmap](#15-scalability-roadmap)
16. [Risks & Mitigations](#16-risks--mitigations)
17. [Content Samples](#17-content-samples)

---

## 1. Project Vision & Problem Statement

### The Problem

People building with AI face a fragmented landscape:
- Raw prompt libraries exist everywhere, but they produce inconsistent results
- There is no single, structured platform offering **outcome-driven workflows** — multi-step AI systems that reliably solve a specific business problem
- Freelancers and agencies lack a professional vehicle to showcase AI expertise in a tangible, credible way

### The Solution: Outflo

Outflo is an **AI Prompt & Workflow Platform** that goes beyond storing prompts. It treats AI as a system-design problem: each piece of content is either a well-structured prompt with clear use-case context, or a full multi-step workflow that chains prompts together to produce a concrete, repeatable business outcome.

**Core positioning:** *"Outcome-driven AI workflows that solve real-world problems"*

This is intentionally **not** another generic prompt dump. Every item on the platform is framed around:
- A specific real-world use case
- A defined output
- Actionable, immediately usable copy

### Dual Purpose

Outflo simultaneously functions as:
1. A **public platform** for discovering and copying AI workflows
2. A **portfolio and lead-generation engine** for the builder to attract freelance/consulting clients

---

## 2. Business Context & Goals

### Primary Objectives

| Goal | How Outflo Serves It |
|---|---|
| Portfolio showcase | Demonstrates AI product engineering from business spec to deployed app |
| Freelance lead generation | "Hire Me" CTA + demonstrated expertise in AI workflows |
| Digital product foundation | Content-driven architecture easily upgrades to paid access |
| Authority building | SEO-optimized content positions the platform as a trusted AI resource |

### Monetization Roadmap

| Phase | Revenue Stream | Description |
|---|---|---|
| Phase 1 (Current) | Freelancing services | AI workflow consulting, automation solutions, prompt engineering |
| Phase 2 | Productized packs | Paid workflow bundles (₹499–₹2,999) |
| Phase 3 | Premium subscriptions | Gated access to exclusive, high-value workflows |
| Phase 4 | Marketplace + SaaS | User-generated content marketplace, API-based tools |

### Key Business Insight

> **Users do not pay for prompts. They pay for results and systems.**

The platform's value proposition is built around this — content is always presented as an outcome-driven system, not a raw text snippet.

---

## 3. Tech Stack & Rationale

### Final Stack

| Layer | Technology | Version |
|---|---|---|
| Framework | Next.js (App Router) | 14.2.5 |
| Language | TypeScript | ^5 |
| Styling | Tailwind CSS | ^3.4.1 |
| Content Parsing (frontmatter) | gray-matter | ^4.0.3 |
| Content Rendering (Markdown → HTML) | remark + remark-html | ^15 / ^16 |
| Deployment | Vercel | — |
| Version Control | GitHub | — |

### Why Next.js over Alternatives

Next.js was chosen over simpler alternatives (Astro, Create React App) based on three core reasons:

**1. Full-stack capability.** While the MVP uses static Markdown, Phase 2 requires API routes, and Phase 3 requires auth and payment flows. Next.js handles all of this in a single framework — no migration needed.

**2. Freelancing credibility.** Next.js is the industry-standard React framework. Demonstrating proficiency in it is directly marketable to clients who build with it.

**3. SSG + ISR flexibility.** Next.js provides Static Site Generation out of the box (critical for performance and SEO), with a clear upgrade path to Incremental Static Regeneration and dynamic rendering as content scales.

### Why Markdown as the Content Layer

- Zero backend overhead in Phase 1 — content lives in the repo itself
- File-based workflow maps directly to a CI/CD pipeline: commit a `.md` file, Vercel rebuilds automatically
- The content schema (YAML frontmatter + body) is human-readable and trivially extensible
- Upgrade path to a database (Supabase) is clean: the same data shape used in frontmatter becomes database columns

---

## 4. Architecture Design

### High-Level Architecture

```
User Browser
     │
     ▼
Next.js Frontend (App Router)
     │
     ├── Static Pages (SSG) ── Markdown Content Layer ── /content/*.md
     │
     └── API Layer (Future) ── Database (Supabase — Phase 2)

GitHub Repository
     │
     └── Vercel Deployment (CI/CD)
```

### Rendering Strategy: Static-First

The entire platform uses **Static Site Generation (SSG)**:

- At build time, Next.js reads all Markdown files from `/content/prompts/` and `/content/workflows/`
- `generateStaticParams()` is called on each dynamic route to pre-render every prompt and workflow page
- The resulting output is a fully static HTML site served from Vercel's CDN edge network

This means:
- Sub-100ms page loads globally
- Zero server costs at scale
- Full crawlability by search engines (pre-rendered HTML, not JavaScript-rendered content)

### Server / Client Component Split

This is the most architecturally significant pattern in the codebase.

| Component | Type | Reason |
|---|---|---|
| `app/page.tsx` | Server Component | Fetches all prompts at build time using Node.js `fs` API |
| `app/workflows/page.tsx` | Server Component | Fetches all workflows at build time |
| `app/prompts/[slug]/page.tsx` | Server Component | Fetches single prompt + generates static params |
| `app/workflows/[slug]/page.tsx` | Server Component | Fetches single workflow + generates static params |
| `HomeClient.tsx` | Client Component | Needs `useState` for search/filter interactivity |
| `WorkflowsClient.tsx` | Client Component | Needs `useState` for search/filter interactivity |
| `PromptCard.tsx` | Client Component | Needs `useState`/`useEffect` for bookmark persistence |
| `CopyButton.tsx` | Client Component | Needs `useState` for copied feedback state |
| `ThemeToggle.tsx` | Client Component | Reads/writes `localStorage` for theme persistence |

The pattern: **Server Components own data fetching and pass serialized data down as props to Client Components that own interactivity.** This prevents client-side data fetching entirely while keeping interactive UI fully functional.

---

## 5. Project Structure

```
outflo/
├── content/                      ← Flat-file CMS
│   ├── prompts/                  ← Each .md = one prompt
│   │   ├── email-marketing-copy.md
│   │   ├── linkedin-thought-leadership.md
│   │   └── seo-blog-post.md
│   └── workflows/                ← Each .md = one multi-step workflow
│       ├── content-creation-pipeline.md
│       └── lead-generation-system.md
│
├── src/
│   ├── app/                      ← Next.js App Router
│   │   ├── layout.tsx            ← Root layout (Header, Footer, BottomNav, dark mode init)
│   │   ├── page.tsx              ← Homepage (Server Component)
│   │   ├── not-found.tsx         ← Custom 404 page
│   │   ├── robots.ts             ← Auto-generated robots.txt
│   │   ├── sitemap.ts            ← Auto-generated XML sitemap
│   │   ├── globals.css           ← Global styles
│   │   ├── prompts/
│   │   │   └── [slug]/
│   │   │       └── page.tsx      ← Dynamic prompt detail page
│   │   └── workflows/
│   │       ├── page.tsx          ← Workflows listing page
│   │       └── [slug]/
│   │           └── page.tsx      ← Dynamic workflow detail page
│   │
│   ├── components/
│   │   ├── HomeClient.tsx        ← Search + filter + grid (Client Component)
│   │   ├── WorkflowsClient.tsx   ← Search + filter + grid for workflows
│   │   ├── WorkflowSteps.tsx     ← Numbered step renderer with per-step copy
│   │   ├── ThemeToggle.tsx       ← Dark/light mode toggle
│   │   ├── cards/
│   │   │   ├── PromptCard.tsx    ← Prompt card with bookmark + copy
│   │   │   └── WorkflowCard.tsx  ← Workflow card
│   │   ├── layout/
│   │   │   ├── Header.tsx        ← Sticky pill nav (desktop) + top bar (mobile)
│   │   │   ├── Footer.tsx        ← Site footer
│   │   │   └── BottomNav.tsx     ← Mobile-only bottom navigation
│   │   └── ui/
│   │       ├── Badge.tsx         ← Tag/filter badge with active state
│   │       └── CopyButton.tsx    ← Clipboard button with feedback animation
│   │
│   ├── lib/
│   │   ├── markdown.ts           ← All content parsing logic
│   │   └── seo.ts                ← Metadata builder utility
│   │
│   └── types/
│       └── index.ts              ← All TypeScript interfaces
│
├── tailwind.config.ts            ← Custom neo-brutalism design tokens
├── next.config.mjs               ← Next.js config
└── package.json
```

---

## 6. Data Model & Content Layer

### TypeScript Interfaces

```typescript
// Base prompt metadata (used in cards and listings)
interface PromptMeta {
  slug: string;
  title: string;
  description: string;
  image?: string;
  tags: string[];
  created_at?: string;
  rawContent: string;   // Original markdown — used by CopyButton directly in cards
}

// Full prompt (used on detail pages)
interface Prompt extends PromptMeta {
  content: string;      // HTML-rendered version for display
}

// Workflow metadata (listings)
interface WorkflowMeta {
  slug: string;
  title: string;
  description: string;
  image?: string;
  tags: string[];
  created_at?: string;
}

// Full workflow with parsed steps
interface Workflow extends WorkflowMeta {
  content: string;          // Full HTML-rendered content
  rawContent: string;       // Original markdown
  steps: WorkflowStep[];    // Parsed individual steps
}

// Individual workflow step
interface WorkflowStep {
  title: string;   // Extracted from ## heading
  content: string; // Raw markdown body of that section
}
```

### Markdown Content Schema

Every content file uses YAML frontmatter:

```markdown
---
title: "Email Marketing Copywriter"
description: "Generate high-converting email copy for any campaign."
image: "/images/email-copy.png"
tags: ["Marketing", "Email", "Copywriting"]
created_at: "2024-01-20"
---

[Content body here]
```

Prompts contain a single-body text. Workflows use `##` headings as step delimiters.

### Markdown Parsing Pipeline (`src/lib/markdown.ts`)

**For Prompts:**
1. `fs.readdirSync(PROMPTS_DIR)` — read all `.md` files at build time
2. `matter(raw)` — split into `data` (frontmatter) and `content` (body)
3. `remark().use(remarkHtml).process(content)` — convert markdown to HTML for rendering
4. Return both `content` (HTML) and `rawContent` (original markdown) — HTML for display, raw for the copy button

**For Workflows — Custom Step Parser:**

```typescript
function parseWorkflowSteps(content: string): WorkflowStep[] {
  const lines = content.split("\n");
  const steps: WorkflowStep[] = [];
  let currentTitle = "";
  let currentLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("## ")) {
      // Flush the previous step when a new ## heading is encountered
      if (currentTitle) {
        steps.push({ title: currentTitle, content: currentLines.join("\n").trim() });
      }
      currentTitle = line.replace(/^## /, "").trim();
      currentLines = [];
    } else {
      currentLines.push(line);
    }
  }
  // Flush the final step
  if (currentTitle) {
    steps.push({ title: currentTitle, content: currentLines.join("\n").trim() });
  }

  return steps;
}
```

This algorithm treats every `##` H2 heading as a step boundary, collecting all lines until the next heading into a single step object. This enables per-step copy buttons and step numbering on the workflow detail page.

---

## 7. Core Feature Deep Dives

### 7.1 Homepage Search & Tag Filtering

**Implementation:** `HomeClient.tsx`

The filtering logic runs entirely client-side using `useMemo` for performance:

```typescript
const filtered = useMemo(() => {
  return prompts.filter((p) => {
    const q = search.toLowerCase();
    const matchSearch =
      q === "" ||
      p.title.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.tags.some((t) => t.toLowerCase().includes(q));
    const matchTag = activeTag === null || p.tags.includes(activeTag);
    return matchSearch && matchTag;
  });
}, [prompts, search, activeTag]);
```

The search matches across title, description, AND tags — so typing "marketing" shows results tagged with marketing as well as those containing the word in their description. The `useMemo` ensures re-filtering only happens when the prompt data, search query, or active tag actually changes.

Tag deduplication happens in the Server Component parent:
```typescript
const allTags = [...new Set(prompts.flatMap((p) => p.tags))].sort();
```

### 7.2 Copy-to-Clipboard with Feedback

**Implementation:** `src/components/ui/CopyButton.tsx`

The component uses the Clipboard API and a timed state reset to provide visual feedback:

```typescript
async function handleCopy() {
  await navigator.clipboard.writeText(text);
  setCopied(true);
  setTimeout(() => setCopied(false), 2000);
}
```

The button renders two visual states: a copy icon when idle, and a checkmark icon for 2 seconds after copying. It supports two modes: `iconOnly` (compact, used on cards) and full text button (used on detail pages).

### 7.3 Bookmarking System

**Implementation:** `PromptCard.tsx`

Bookmarks are persisted to `localStorage` and read back on component mount via `useEffect`:

```typescript
function getBookmarks(): string[] {
  try {
    return JSON.parse(localStorage.getItem("bookmarks") ?? "[]");
  } catch { return []; }
}

useEffect(() => {
  setBookmarked(getBookmarks().includes(prompt.slug));
}, [prompt.slug]);
```

The `try/catch` around the localStorage read handles cases where the browser blocks storage access (private/incognito mode on certain browsers). The `useEffect` is used intentionally rather than initializing state directly — this prevents a hydration mismatch between the server render (where `localStorage` doesn't exist) and the first client render.

### 7.4 Workflow Detail Page

**Implementation:** `app/workflows/[slug]/page.tsx` + `WorkflowSteps.tsx`

The workflow detail page builds a `Copy All Steps` text by concatenating all steps with separators:
```typescript
const allStepsText = workflow.steps.map((s, i) =>
  `Step ${i + 1}: ${s.title}\n\n${s.content}`
).join("\n\n---\n\n");
```

The `WorkflowSteps` component renders each step with a numbered badge, its title, per-step copy button, and the raw prompt content in a monospace pre block — intentionally raw (not HTML-rendered) so the copy output is clean, unformatted text ready to paste into any AI tool.

### 7.5 JSON-LD Structured Data

Both detail page types inject `application/ld+json` scripts with schema-appropriate types:

- Prompt pages → `schema.org/Article`
- Workflow pages → `schema.org/HowTo` with `HowToStep` entries

```typescript
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "HowTo",
  name: workflow.title,
  step: workflow.steps.map((s, i) => ({
    "@type": "HowToStep",
    position: i + 1,
    name: s.title,
    text: s.content,
  })),
};
```

This enables rich results in Google Search (e.g., step-by-step cards directly in SERPs).

---

## 8. UI/UX Design System

### Neo-Brutalism Design Language

Outflo uses a Neo-Brutalism aesthetic — a modern design trend characterized by bold borders, flat offset shadows, high contrast, and raw geometric shapes. This was chosen because:
1. It creates immediate visual distinctiveness in a crowded market
2. It communicates confidence and directness, matching the "get results fast" brand voice
3. It is highly legible and optimized for scan-reading (useful for a content-heavy platform)

### Custom Tailwind Design Tokens

```typescript
// tailwind.config.ts
colors: {
  cream: "#F5F0E8",          // Page background (warm off-white)
  neo: {
    black: "#0D0D0D",        // Near-black for text and borders
    yellow: "#FFE500",       // Brand accent — used for highlights, CTAs, active states
    white: "#FFFFFF",
  },
},
boxShadow: {
  neo: "4px 4px 0px #0D0D0D",          // Standard neo-brutalist shadow
  "neo-lg": "6px 6px 0px #0D0D0D",    // Hover/elevated state
  "neo-sm": "2px 2px 0px #0D0D0D",    // Pressed/active state
  "neo-white": "4px 4px 0px #FFFFFF", // Dark-mode variants
  ...
},
```

### Hover Interactions

Cards use a micro-animation on hover:
```
hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-neo-lg
```

This creates the illusion of the card lifting off the page — consistent with the neo-brutalism "physical paper" metaphor.

### Mobile-First Responsive Layout

- Desktop: sticky pill-shaped navigation bar centered at the top
- Mobile: simplified top bar (logo + theme toggle only) + a fixed bottom navigation tab bar
- Grid: 1 column → 2 columns → 3 columns across breakpoints (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`)
- Content padding: percentage-based (`px-[10%] sm:px-[6%] lg:px-[12%]`) scales fluidly

---

## 9. SEO Architecture

### Metadata System (`src/lib/seo.ts`)

All pages use a single centralized `buildMetadata()` utility that generates:
- Page `<title>` in `"Page Title | Outflo"` format
- `<meta description>`
- OpenGraph tags (title, description, URL, image, site name)
- Twitter Card tags (`summary_large_image`)
- Canonical URL

```typescript
export function buildMetadata({ title, description, image, path }) {
  return {
    title: title ? `${title} | Outflo` : "Outflo",
    openGraph: { ... },
    twitter: { card: "summary_large_image", ... },
    alternates: { canonical: url },
  };
}
```

### Dynamic Metadata on Detail Pages

Each prompt and workflow page calls `generateMetadata()` — a Next.js convention for per-page metadata generation:

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const prompt = await getPromptBySlug(params.slug);
  return buildMetadata({
    title: prompt.title,
    description: prompt.description,
    image: prompt.image,
    path: `/prompts/${prompt.slug}`,
  });
}
```

### Auto-Generated Sitemap & Robots

`app/sitemap.ts` exports a function that Next.js automatically serves at `/sitemap.xml`. It dynamically reads all prompts and workflows and generates sitemap entries with:
- `lastModified` from the content's `created_at` field
- Priority values: homepage (1.0), workflows listing (0.9), individual pages (0.8)
- `changeFrequency`: daily for listings, monthly for individual pages

`app/robots.ts` generates `/robots.txt` allowing all crawlers and pointing to the sitemap URL.

---

## 10. Performance Optimizations

| Technique | Implementation | Impact |
|---|---|---|
| Static Site Generation | `generateStaticParams()` on all dynamic routes | All pages pre-rendered at build time — zero server computation on request |
| No client-side data fetching | Server Components fetch all data | Eliminates loading states for content |
| `useMemo` for filtering | Filters only recompute on dependency changes | Smooth 60fps filtering even with large content sets |
| Font subsetting | `Inter` loaded with `subsets: ["latin"]` | Reduces font payload |
| Next.js `<Image>` | Used for prompt images | Auto-resizing, lazy loading, WebP conversion |
| Code splitting | Next.js automatic per-route splitting | Only loads JS needed for the current page |
| Tailwind CSS purging | `content` array in tailwind config | Removes unused CSS classes in production build |

---

## 11. Component Architecture

### Design Principles

1. **Single responsibility** — each component has exactly one job
2. **Props-driven** — components are pure functions of their inputs (no internal data fetching)
3. **Composability** — `CopyButton` and `Badge` are used across multiple surfaces without modification

### Component Dependency Tree

```
RootLayout
├── Header (Client — needs usePathname for active nav state)
├── main
│   ├── HomePage (Server)
│   │   └── HomeClient (Client)
│   │       ├── Badge (UI)
│   │       └── PromptCard (Client)
│   │           ├── Badge (UI)
│   │           └── CopyButton (UI, Client)
│   ├── WorkflowsPage (Server)
│   │   └── WorkflowsClient (Client)
│   │       ├── Badge (UI)
│   │       └── WorkflowCard (Client)
│   ├── PromptPage (Server — /prompts/[slug])
│   │   ├── Badge (UI)
│   │   └── CopyButton (UI, Client)
│   └── WorkflowPage (Server — /workflows/[slug])
│       ├── Badge (UI)
│       ├── CopyButton (UI, Client)
│       └── WorkflowSteps (Client)
│           └── CopyButton (UI, Client)
├── Footer
└── BottomNav (Client — needs usePathname for active tab state)
```

---

## 12. Routing & Navigation

### File-Based Routing (Next.js App Router)

| URL | File | Type |
|---|---|---|
| `/` | `app/page.tsx` | Server Component |
| `/workflows` | `app/workflows/page.tsx` | Server Component |
| `/prompts/[slug]` | `app/prompts/[slug]/page.tsx` | Server Component + SSG |
| `/workflows/[slug]` | `app/workflows/[slug]/page.tsx` | Server Component + SSG |
| `/sitemap.xml` | `app/sitemap.ts` | Auto-generated |
| `/robots.txt` | `app/robots.ts` | Auto-generated |

### Slug Generation

Slugs are derived directly from filenames:
- File: `content/prompts/email-marketing-copy.md`
- Slug: `email-marketing-copy`
- URL: `/prompts/email-marketing-copy`

No separate slug registry is needed — the filesystem is the source of truth.

---

## 13. Dark Mode Implementation

Dark mode is implemented using Tailwind's `class` strategy — toggled by adding/removing a `dark` class on the `<html>` element.

### Flash Prevention

A critical UX detail: without intervention, the page renders in light mode for one frame on load before JavaScript reads the stored preference and applies the dark class. This causes a visible flash. The solution is an inline script injected into `<head>` **before** any React hydration:

```html
<script>
  try {
    const t = localStorage.getItem('theme');
    if (t === 'dark') { document.documentElement.classList.add('dark') }
  } catch(_) {}
</script>
```

This runs synchronously during the browser's initial HTML parse, before any CSS or JS files load, eliminating the flash entirely. The `try/catch` handles storage access errors gracefully.

### Theme Toggle Component

The `ThemeToggle` component reads the initial theme from `localStorage` on mount, renders the appropriate icon, and on click toggles the `dark` class on `document.documentElement` while persisting the new preference.

---

## 14. Deployment & CI/CD

### Pipeline

```
Developer writes .md file
        │
        ▼
git commit + push to GitHub
        │
        ▼
Vercel detects push → triggers build
        │
        ▼
Next.js reads all Markdown files (fs API during build)
        │
        ▼
Generates all static HTML pages
        │
        ▼
Deploys to Vercel CDN edge network
        │
        ▼
Live website updated globally
```

### Environment Variables

| Variable | Usage | Example |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | Canonical URLs, sitemap, OG images | `https://outflo.vercel.app` |

---

## 15. Scalability Roadmap

### Phase 1 — Current (MVP)

- Static Markdown content
- SSG + Vercel CDN
- No backend, no database
- Cost: $0 (Vercel free tier)

### Phase 2 — Dynamic Backend

- Add Next.js API routes
- Integrate Supabase (PostgreSQL) to replace file-based content
- Enable CMS-style content management without code deploys
- ISR (Incremental Static Regeneration) for content updates without full rebuild

### Phase 3 — Monetization

- Supabase Auth for user accounts
- Stripe integration for paid workflow packs
- Content gating: free vs. premium tier
- User dashboard with saved/bookmarked content

### Phase 4 — Ecosystem

- User-generated content marketplace
- API endpoints for programmatic prompt access
- SaaS tooling for teams (workflow builder, prompt testing)
- Analytics dashboard

---

## 16. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Low content differentiation | Platform looks like another prompt dump | Maintain strict outcome-focus; workflows > prompts ratio |
| Static limitations at scale | Hundreds of prompts slow build times | Move to ISR + database in Phase 2; acceptable up to ~500 pages |
| Monetization friction | Users expect prompts to be free | Lead with freelancing/services CTA before paid content |
| SEO competition | AI prompt space is crowded | Niche down to specific use-cases; leverage JSON-LD for rich results |
| Flash of unstyled content (FOUC) | Dark mode flash damages UX | Inline `<head>` script prevents flash (implemented) |

---

## 17. Content Samples

### Prompt Example: Email Marketing Copywriter

**File:** `content/prompts/email-marketing-copy.md`
**Tags:** Marketing, Email, Copywriting
**Use case:** Generates structured email campaigns with subject lines, preview text, body, CTA, and P.S. — filled with role-based AI instructions and output format specification.

### Workflow Example: Content Creation Pipeline

**File:** `content/workflows/content-creation-pipeline.md`
**Steps:** 5 steps (Research & Ideation → Outline → First Draft → Edit & Optimize → Repurpose & Distribute)
**Use case:** Takes a user from a raw content idea to published, platform-distributed content using a chain of AI prompts — each step building on the output of the last.

---

*Report generated: June 2026*
