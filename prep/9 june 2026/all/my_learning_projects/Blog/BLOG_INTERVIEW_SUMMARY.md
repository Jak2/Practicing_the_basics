# Blog — Markdown Documentation Engine: Interview Summary

> **Role target:** Backend Python SWE / AI Engineer  
> **Framing for interview:** Use this project to demonstrate full-stack breadth — build pipelines, algorithmic thinking, zero-dependency frontend design. Don't lead with it; bring it up when the conversation turns to frontend systems or "what else have you built?"

---

## 30-Second Elevator Pitch

I built a static documentation site generator — think a minimal version of Docusaurus or VitePress — using Astro. You drop Markdown files into a folder, run a build, and get a fully-featured docs website with auto-generated sidebar navigation, client-side full-text search, a scroll-spy table of contents, and dark mode. No backend, no database, no runtime server. The entire `dist/` output is static HTML that deploys to any CDN in under a minute.

---

## 2-Minute Structured Pitch

**The goal:** Most documentation tools either require a heavyweight CMS backend or are tightly coupled to a paid platform. I wanted to understand how to build the same experience — folder-based routing, search, navigation — from scratch with zero runtime infrastructure.

**What I built:** An Astro-based static site generator where the folder structure in `src/content/docs/` becomes the URL structure and sidebar navigation automatically. The core insight is Astro's build-time model: everything that can be computed at build time — the sidebar tree, the search index, the route manifest — is. Nothing is deferred to runtime. The resulting site has no server-side attack surface, no API dependencies, and loads instantly from a CDN.

**The interesting technical pieces:** The sidebar builds itself by running `import.meta.glob()` at build time to scan all Markdown files, converting file paths to URL routes, then recursively building a nested tree structure. The search engine is ~80 lines of vanilla JavaScript with weighted term scoring and match highlighting — no external library. The table of contents uses the `IntersectionObserver` API with a calibrated `rootMargin` to highlight the heading you're currently reading as you scroll.

**Why it's relevant:** It demonstrates I understand build pipelines, can design systems with a clear build-time vs. runtime separation, and can implement algorithmic logic (tree building, search scoring) in vanilla JS without reaching for a library as the default answer.

---

## Technical Highlights

### `import.meta.glob()` as a build-time filesystem API

This is the key Vite/Astro primitive that makes the whole project work. At build time, `import.meta.glob('/src/content/docs/**/*.md', { eager: true })` returns a map of every matching file path to its parsed module object — frontmatter, headings, raw content, all of it. No runtime file system access, no API calls. The sidebar and search index both consume this map:

- **Sidebar:** converts file paths to routes, builds a nested tree, renders collapsible `<details>` navigation
- **Search index:** extracts titles, headings, and 200-character content excerpts from every page and serializes them into a JSON blob embedded in every page's HTML

This pattern — "scan the filesystem at build time, bake the result into the output" — is directly analogous to how many backend code generation pipelines work. You compute once, pay nothing at runtime.

### Custom search scoring algorithm

Rather than importing Lunr.js or Fuse.js, I wrote the search engine from scratch to understand what these libraries actually do:

```
Query: "getting started install"
  → split into terms: ["getting", "started", "install"]
  → for each page in the search index:
      score += 10 for each term found in title
      score += 5  for each term found in headings
      score += 2  for each term found in content excerpt
  → filter score > 0, sort descending, take top 8
  → highlight matches with <mark> tags via regex
```

Debounced at 150ms on input. Results rendered as a keyboard-navigable dropdown. XSS-safe: all user input is HTML-escaped before being inserted as `innerHTML`. The key insight is that weighted scoring is the core of any text search algorithm — Lucene/Elasticsearch do the same thing at scale with more sophisticated term weighting (TF-IDF, BM25), but the underlying idea is identical.

### IntersectionObserver for scroll spy

The table of contents highlights the active heading as you scroll. I used `IntersectionObserver` rather than a scroll event listener because it fires only when visibility changes — not on every pixel of scroll — making it significantly more performant on long pages.

The calibration detail: `rootMargin: '-80px 0px -80% 0px'` shrinks the detection zone to the top 20% of the viewport (minus the 64px fixed navbar). This means the "active" heading is always the one you're currently reading, not one approaching from below.

### CSS scroll offset for fixed headers

Clicking a table of contents link was jumping to headings but landing them behind the sticky 64px navbar — a classic fixed-header problem. The CSS-native fix:

```css
html { scroll-padding-top: 4rem; }   /* adjusts scroll destination for anchor links */
[id] { scroll-margin-top: 4rem; }    /* adjusts scroll destination for the element itself */
```

Two properties, different purposes: `scroll-padding-top` shifts where the browser considers "top of viewport" when scrolling to an anchor. `scroll-margin-top` shifts the element's own scroll target. You need both for complete coverage across browsers.

---

## Key Design Decisions

### Embed search index in HTML vs. load as a separate file

The search index is serialized as a `<script type="application/json">` tag inside every page's HTML rather than fetched as a separate `/search-index.json` file. This means search works immediately with zero extra network requests, even with no CDN edge cache hit.

The trade-off: every page carries the full index. For a docs site with 50+ pages this adds overhead — at that scale I'd move to a lazy-loaded JSON file or a dedicated search service like Pagefind. For a learning project, the simpler approach is correct.

### No external search library

The 80-line vanilla implementation demonstrates the concept clearly and adds zero dependencies. A library like Fuse.js would have hidden the algorithm. When an interviewer asks "how does your search work?" I can explain it in two sentences because I wrote every line of it.

### Native `<details>` for sidebar collapsing

Collapsible sidebar sections use the HTML `<details>`/`<summary>` elements with `open={hasActiveChild}` for auto-expansion. Zero JavaScript. The browser handles open/close state natively. This was a deliberate choice to avoid the instinct to reach for a state management solution where a browser primitive already exists.

### DOM-clone mobile sidebar

The mobile overlay clones the desktop sidebar's HTML (`sidebar.innerHTML`) rather than maintaining a separate mobile nav component. The desktop and mobile navs are always identical with no shared state layer or duplicated template. A pragmatic choice: one source of truth, no sync bugs.

---

## What It Demonstrates (for a Backend/AI Role)

This project is evidence of full-stack range, not frontend expertise. The relevant signals:

- **Build pipeline thinking** — understanding the build-time vs. runtime split is the same mental model you apply when designing data processing pipelines: compute what you can offline, serve the result cheaply
- **Algorithmic implementation** — the sidebar tree builder, search scorer, and TOC scroll spy are all small algorithms written from scratch, which shows comfort with data structure manipulation and DOM APIs without framework abstractions
- **Zero-dependency discipline** — choosing `<details>` over a JS accordion, vanilla search over a library, CSS scroll offset over a JS scroll handler. Knowing when not to add a dependency is an underrated engineering skill
- **Static site deployment** — understanding the CDN-first deployment model (build once, serve from edge) is relevant to any system that serves static content at scale

---

## Known Limitations

| Limitation | What I'd say |
|---|---|
| **Search index in every page** | Scales linearly with doc count. For large sites I'd move to a separately fetched JSON index or use Pagefind (a proper static search tool). |
| **Sidebar only 2 levels deep** | The tree builder handles sections and their direct children. A third nesting level isn't rendered. Extending `buildTree()` to recurse indefinitely is straightforward — I just didn't need it. |
| **Shallow content excerpts** | Search uses the first 200 characters per page. Content buried deep in a long page won't surface. Full-page indexing with chunking (same pattern as FAISS in EMS 2.0) would fix this. |
| **No build-time image optimization** | Images in Markdown aren't processed through Astro's image optimization pipeline. A production docs site would want responsive image generation at build time. |

---

## What I Genuinely Learned

- **Build-time computation is underused.** Anything you can precompute — navigation trees, search indexes, route manifests — should be precomputed. The cost is at build time, not at every user request. This is the same principle behind server-side rendering, pre-aggregated analytics, and offline embedding generation.

- **`getStaticPaths()` is the SSG contract.** Static site generators require you to declare every valid route at build time. There is no "figure it out at request time." This constraint forces upfront clarity about what pages exist — which is actually a useful discipline.

- **Browser APIs are more capable than most developers use.** `IntersectionObserver`, `<details>`, `scroll-padding-top`, `localStorage`, `matchMedia` — these solved every UX problem in this project without a single runtime dependency. The instinct to reach for a library first is worth questioning.

- **A backend is not always the answer.** When content is structured, read-only, and can be rebuilt on change, a static site generator outperforms a CMS on every axis: speed, cost, security, deployment simplicity. Recognizing when infrastructure is unnecessary is as valuable as knowing how to build it.
