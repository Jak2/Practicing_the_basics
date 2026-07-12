# Blog / Docs Site Generator — Interview Q&A

**Resume bullet:** *"Blog / Docs Site Generator: Drop Markdown files in a folder, get a fully navigable documentation site instantly. No routing config, no frontend code — just write. Stack: Astro, Markdown."*

**Project (internal name):** `Blog` — Markdown Documentation Engine. Astro 3.5+, Tailwind 3.3+, vanilla JS. No backend, no database, no runtime server.

---

## READ THIS FIRST — where this project is actually attackable

| # | The question that can genuinely hurt | Why it hurts | Your one-line posture |
|---|---|---|---|
| 1 | **"Why is this on your resume next to a production AI agent runtime? What does it actually demonstrate?"** | It's the smallest project you have and the interviewer knows it. If you inflate it, you poison your good projects. | "It demonstrates restraint. It's defined by what it refuses to have — no config, no CMS, no database, no framework. Knowing where to stop is the skill I'm showing." |
| 2 | **"Why Astro? Why not Next.js / Hugo / Jekyll / Docusaurus?"** | If you say "it was popular" you're dead. Each alternative has a real tradeoff you must name. | "I wanted zero JS by default and static output. Docusaurus ships React to the client for a page that's just text. Astro's model is: build-time by default, JS only where I ask." |
| 3 | **"You embedded the full search index into every page's HTML. That's O(pages²) bytes. Why?"** | It's a genuinely questionable call and it's in your own report as a tradeoff. | "It's a deliberate tradeoff with a known ceiling: zero network round-trips, index always in sync, and it breaks past ~50 pages. Chunking to a separate JSON is the documented upgrade path." |
| 4 | **"When is this the WRONG tool? Talk me out of it."** | Seniority test. If you can't disqualify your own tool, you don't understand it. | "Anything with auth, personalization, user-generated content, or thousands of pages with slow builds. It's read-only structured content or nothing." |
| 5 | **"'No routing config' — what's the actual mechanism? Don't hand-wave."** | This is the resume claim. If you can't explain the mechanism, the bullet is a lie. | "`import.meta.glob()` at build time enumerates the markdown files, `getStaticPaths()` turns each file path into a route param, and Astro pre-renders one HTML file per route into `dist/`." |
| 6 | **"You wrote your own search engine instead of using Lunr/FlexSearch. Isn't that exactly the over-engineering you claim to avoid?"** | It looks like a contradiction with your own restraint story. | "Inverted: the library IS the heavier option here. ~80 lines of vanilla JS with weighted scoring beats adding a dependency and a build step for a 50-page site." |
| 7 | **"Your search is a substring-match scorer over 200-char excerpts. It'll miss content buried in long pages. Do you know that?"** | Tests whether you know your own system's failure mode. | "Yes, and it's in my limitations list. The index is shallow by construction — title +10, heading +5, excerpt +2. Deep content is unreachable. That's the price of a build-time index with no library." |

---

## Section 1 — Framing (answer these before you're asked)

**Q1. Why is this project on your resume, sitting next to a production AI agent runtime? What does it demonstrate that the bigger projects don't?**

> Honestly? It demonstrates restraint, and I put it there on purpose. My other projects show that I can build something large. This one shows I know when *not* to. It's a project defined by what it refuses to have: no backend, no database, no CMS, no routing config, no frontend framework shipped to the client, no search library. The interesting engineering isn't in what I added — it's in every decision to not add. Most engineers I've worked with can build the big thing. Fewer can identify the minimum viable thing and then stop. I think that's a real skill and this is my evidence for it.

**Q2. That sounds like a rationalization for a small project.**

> It's a small project. I'm not going to pretend it's more. It's a learning project — I've labelled it that in my own report. What I'd push back on is the idea that size correlates with judgment. The core insight here — that documentation is *structured, read-only content*, so the entire class of backend problems is optional — is the kind of insight that saves a team six months. I'd rather show you a small system where every decision was deliberate than a large one where half of them were inherited.

**Q3. Give me the 30-second version of what it is.**

> You drop a `.md` file into `src/content/docs/`. At build time, Astro discovers it with `import.meta.glob()`, `getStaticPaths()` generates a route for it, the sidebar tree is built from the folder structure, the search index is built from the titles and headings, and the whole thing is compiled into static HTML in `dist/`. You upload `dist/` to any CDN. There is no server. The only JS that runs in the browser is dark mode, search, the mobile menu, and a scroll-spy for the table of contents.

**Q4. Who was the user? Did anyone actually use it?**

> [FILL: was this used by anyone besides you? deployed anywhere? if not, say "it was a learning project — I was the user" and do not embellish]

**Q5. How long did it take?**

> [FILL: actual build duration — the report is dated 2026-06-23 but does not state elapsed time]

---

## Section 2 — Architecture

**Q6. Walk me through the build.**

> `npm run build`. Astro starts, and every `.astro` component's frontmatter script runs on the server, once. Three things read the content directory via `import.meta.glob('/src/content/docs/**/*.md', { eager: true })` independently: `Sidebar.astro` builds the nav tree from file paths, `Navbar.astro` builds the search index from titles/headings/excerpts, and `pages/docs/[...slug].astro`'s `getStaticPaths()` enumerates the routes. Each page then renders through `BaseLayout.astro`, which assembles navbar, sidebar, content and TOC. Output is one static HTML file per markdown file in `dist/`.

**Q7. Walk me through a request.**

> There is no request in the server sense. A user hits `/docs/getting-started/install`; the CDN serves a pre-built HTML file that already contains the sidebar, the content, the TOC, and the search index. The browser then runs a handful of small vanilla scripts: the dark-mode initializer (synchronously, before first paint), the search handler, the mobile menu, and the `IntersectionObserver` scroll spy.

**Q8. Three separate components each call `import.meta.glob()` over the same directory. Isn't that three full scans of the content tree?**

> Yes, and it's a real inefficiency — the sidebar, the navbar's search index, and `getStaticPaths()` each glob independently. It's cheap because it's build-time and Vite caches the module graph, but architecturally that content tree should be built once and shared. Astro's own **Content Collections** API is the right answer for that — a single typed collection with a schema, queried by every component. [FILL: confirm whether you knew about Content Collections at the time or discovered them later — do not claim a decision you didn't make]

**Q9. So you're not using Astro Content Collections?**

> No — I'm using raw `import.meta.glob()` over `src/content/docs/`. The directory is named like a collection but I'm reading it as files, not through the collection API. The cost is that I get no frontmatter schema validation: if someone writes `titel:` instead of `title:`, nothing errors — the page silently falls back to a filename-derived title. A Zod schema on a Content Collection would have failed the build. That's the strongest single upgrade this project has available.

**Q10. What's in `BaseLayout.astro`?**

> The master template: `<head>`, the navbar, the responsive 3-column grid, and the slots. It exposes a default `<slot />` for the article body and a named `<slot name="toc" />` for the right rail. The page does `<TableOfContents slot="toc" headings={headings} />` and the layout never has to know what a TOC is. That's Astro's version of the children/composition pattern.

**Q11. Why does the dark-mode script have to run before first paint?**

> Because otherwise you get a flash of the wrong theme. The script in `BaseLayout.astro` runs synchronously in the head, reads `localStorage.getItem('theme')`, falls back to `window.matchMedia('(prefers-color-scheme: dark)')`, and adds the `dark` class to `<html>` before the browser paints anything. If you defer it, the user sees white, then black.

---

## Section 3 — Routing and "no config"

**Q12. Explain "no routing config" precisely. What is the mechanism?**

> One file: `src/pages/docs/[...slug].astro`. The `[...slug]` is Astro's rest parameter — it captures everything under `/docs/`. Because Astro is a static generator, it can't discover routes lazily, so that file exports `getStaticPaths()`. That function globs `/src/content/docs/**/*.md`, and for each file path strips the prefix and the `.md` suffix, collapses `/index` to the parent route, and returns `{ params: { slug } }`. Astro pre-renders one HTML page per returned object. Folder structure *is* URL structure — nobody ever edits a route table.

**Q13. What happens to `index.md` inside a folder?**

> It collapses to the parent route. `getting-started/index.md` becomes `/docs/getting-started` — the section landing page. That's handled in the path-to-route conversion, not by any special config.

**Q14. And the root `/docs` page?**

> That's the edge case in `getStaticPaths()`. When the computed slug string is empty, I return `{ params: { slug: undefined } }` — an undefined rest param is how Astro represents "the bare route with nothing after it". If you return an empty string instead, it doesn't match.

**Q15. You hit two build errors on this route. Tell me about them.**

> The first was blunt: `[...slug].astro` wouldn't build at all because `getStaticPaths()` was missing. Astro's SSG mode can't resolve a rest param without an explicit path manifest — there's no runtime to ask. Adding the glob-driven `getStaticPaths()` fixed it. The second was subtler and I got it wrong for a while: I assumed `[...slug]` gave me an *array* of path segments — `['getting-started', 'install']` — so nested pages broke. It doesn't. It captures a single string containing the whole remaining path. Once I treated it as a string and used `.replace()` / `.split()` on it instead of array indexing, nested routes worked.

**Q16. That second bug — how would you have caught it faster?**

> By reading the framework's route-param contract before writing code against my assumption of it. It's the classic failure: the flat routes worked, which "confirmed" my mental model, and only nesting exposed that the model was wrong. A single nested fixture page from day one would have caught it in minutes.

---

## Section 4 — The sidebar

**Q17. How does the sidebar get built?**

> Four steps in `Sidebar.astro`, all at build time. Scan: `import.meta.glob('/src/content/docs/**/*.md', { eager: true })`. Convert: each file path becomes `{ route, title, order }` — strip prefix, strip `.md`, collapse `/index`. Build: `buildTree()` splits each route into segments and walks a nested object, creating nodes as it goes, hanging the page metadata off `__meta`. Render: nodes with children become `<details>` with a `<summary>`, leaves become `<a>`.

**Q18. Why `<details>` instead of a JS accordion?**

> Because `<details>`/`<summary>` is a native collapsible and it costs zero JavaScript. I set `open={hasActiveChild(node)}` at build time so the section containing the current page renders already expanded. The only CSS I needed was `details summary::-webkit-details-marker { display: none }` to hide the browser's default triangle so I could use my own chevron SVG. A JS accordion would have been more code, more state, and it wouldn't work before hydration.

**Q19. How does the sidebar know which page is active — there's no server and no client state?**

> `Astro.url.pathname` is available at build time for each generated page. `isActive()` compares it to the node's route; `hasActiveChild()` walks the node's descendants. Because each page is rendered independently, each page's HTML has its own correct sidebar baked in. There's no runtime active-state logic at all.

**Q20. What controls the ordering?**

> Frontmatter `order`, read by `Sidebar.astro`, defaulting to `999` so anything unlabelled sorts last. It's a per-section sort within the tree.

**Q21. Limitation — how deep does the sidebar nest?**

> Two levels. The tree *builder* handles arbitrary depth, but the *renderer* only draws sections and their direct children. Three-plus levels of nesting silently don't render. It's on my known-limitations list, and it's a renderer fix, not an architecture fix.

**Q22. "Silently don't render" — that's a bad failure mode.**

> Agreed. Content disappears with no error. The right fix is either recursion in the renderer or, at minimum, a build-time warning when the tree is deeper than the renderer can draw. Failing loudly at build time is the whole point of a build step and I didn't take it here.

---

## Section 5 — Search

**Q23. Static sites make search genuinely hard. How did you do it?**

> Two phases. At build time, `Navbar.astro` globs every markdown module and extracts a `SearchEntry` per page: the title (frontmatter, or derived from filename), the headings array from Astro's `getHeadings()`, and a 200-character text excerpt from `rawContent()` with markdown/HTML stripped. That array is serialised to JSON and embedded in the page as `<script type="application/json" id="search-data">`. At runtime, the client script `JSON.parse`s that element's `textContent` — no fetch — and on input, debounced 150ms, splits the query into terms and scores every entry.

**Q24. What's the scoring function?**

> Weighted term matching. Per query term: title match +10, heading match +5, content-excerpt match +2. Then filter `score > 0`, sort descending, take the top 8, render the dropdown with `highlightMatch()` wrapping hits in `<mark>` tags. `Ctrl+K` / `Cmd+K` focuses the box, `Escape` closes it.

**Q25. Why not Lunr.js, FlexSearch, or Fuse.js?**

> Because the library is the *heavier* choice at this scale, not the lighter one. My implementation is about 80 lines of vanilla JS. A library gets me stemming, fuzzy matching and a proper inverted index — real wins on a big corpus — at the cost of a dependency, a bundle, and an index format I'd have to build and ship. On a sub-50-page docs site, weighted substring scoring over titles and headings finds the page. I'd swap to FlexSearch the moment the corpus grew or someone asked for typo tolerance. That's the trigger, and I know what it is.

**Q26. Why embed the index in every page instead of fetching one JSON file?**

> Deliberate tradeoff, and it's the most attackable thing in the project. Embedding means: no extra network request, search works on first keystroke with nothing to wait for, and the index can never be stale relative to the page because they're built together. The cost is that every page's HTML carries the full index — so total bytes shipped grow with pages × index size. At under 50 pages that's noise. At 500 it's indefensible, and the fix is already scoped: move the index to a separate JSON, fetch it on first search interaction, cache it.

**Q27. So you shipped something you know doesn't scale.**

> I shipped something appropriate for its size with a known ceiling and a written upgrade path. The alternative — building the chunked, lazily-fetched index up front for a site that has a dozen pages — is speculative engineering. What I'd defend is not the choice, it's that the choice was *made*, not defaulted into, and that I can tell you exactly when it breaks.

**Q28. What's the deepest weakness of the search itself?**

> The index is shallow: 200 characters of excerpt per page. If the thing you're searching for is in paragraph nine of a long page, and it isn't in the title or a heading, search will not find it. That's not a bug, it's the shape of the index. Fixing it means indexing full page text, which makes the embed-in-every-page decision immediately untenable — the two limitations are coupled.

**Q29. You're injecting matched text into `innerHTML`. Is that an XSS hole?**

> That was the concern, and it's why `escapeHtml()` runs on the matched text before it goes into `innerHTML` — the `<mark>` tags are the only markup I add, and everything else from the index is escaped first. The content is also all first-party markdown from the repo, so the threat model is thin, but I didn't want an unescaped-innerHTML pattern sitting in the codebase regardless.

**Q30. Why 150ms debounce?**

> [FILL: was 150ms measured/tuned, or picked as a common default? Do NOT claim you benchmarked it if you didn't — "it's the standard human-perception-of-instant threshold and I didn't tune it further" is a fine, honest answer]

---

## Section 6 — Table of contents / scroll spy

**Q31. How does the TOC get its headings?**

> The page passes them down. `[...slug].astro` calls Astro's `getHeadings()` on the markdown module, which returns `{ depth, slug, text }` objects, and passes that as a `headings` prop into `<TableOfContents slot="toc" />`. The component renders h1–h3, indented by depth. I also prepend the frontmatter title as a synthetic h1 so the page title is always the first TOC entry.

**Q32. Explain the scroll spy.**

> `IntersectionObserver`, observing every `h1, h2, h3` inside `.docs-content`. When a heading intersects, I find the TOC link with the matching `href="#slug"` and move the active class to it. I use `IntersectionObserver` rather than a scroll listener because it only fires when visibility actually changes, not on every scroll tick — a scroll handler here would be doing work sixty times a second to answer a question that changes once every few seconds.

**Q33. Your `rootMargin` is `'-80px 0px -80% 0px'`. Defend every number.**

> The `-80px` top offset is the sticky navbar — the navbar is 64px and I want the detection line just below it, not underneath it, or the heading currently hidden behind the bar would count as "visible". The `-80%` bottom offset shrinks the intersection zone to the *top 20%* of the viewport. Without it, every heading currently on screen intersects at once and the "active" heading jitters between them — with it, the active heading is the one you're actually reading at the top of your view, not one three screens down.

**Q34. Bug: clicking a TOC link appeared to do nothing. What happened?**

> The anchor jump worked perfectly — it scrolled the heading to the exact top of the viewport, which is precisely where the 64px sticky navbar is. The heading landed behind the navbar, so visually nothing happened. The root cause is that CSS anchor scrolling targets the element's top edge with no concept of a fixed header. The fix is two CSS-native properties: `html { scroll-padding-top: var(--navbar-height) }` moves where the browser considers the "top" of the scrollport, and `[id] { scroll-margin-top: var(--navbar-height) }` applies the offset to the target elements themselves. Both point at one custom property, `--navbar-height: 4rem`, so the navbar height is defined in exactly one place.

**Q35. Why both properties? Isn't one enough?**

> They cover different entry paths. `scroll-padding-top` on `<html>` handles browser-driven anchor navigation into the scrollport. `scroll-margin-top` on the targets handles programmatic and link-driven scrolls to the element — which is what the TOC links and the search-result links do. Setting both means every route to a heading — URL hash, TOC click, search result — lands with the heading visible.

---

## Section 7 — Design decisions (the ones you'll be pushed on)

**Q36. Why Astro and not Next.js?**

> Next.js is a React framework with static export bolted on. Astro is a static generator with optional interactivity bolted on. For a documentation site — text, links, a bit of chrome — the Next.js default of shipping a React runtime and hydrating a component tree is paying a bundle for nothing. Astro's default is zero JS to the client; you opt into interactivity per island. My site's client JS is four small vanilla scripts, and that's the whole payload. Choosing Next here would mean fighting the framework's defaults for every page.

**Q37. Why not Hugo? It's faster than anything.**

> It is — Hugo's build speed is genuinely in another class, and if I had 10,000 pages that's what I'd reach for. Two reasons I didn't: Go templates for anything interactive are painful, and I wanted the option of dropping a real component in without leaving the templating language. Astro gave me the same static output with a component model I could actually build a search box and a scroll spy in. Hugo's advantage — raw build throughput — is an advantage at a scale this project doesn't have.

**Q38. Why not Jekyll?**

> Same family of reasons, worse on every axis for me: slower builds, a Ruby toolchain I didn't want, and the ecosystem's centre of gravity is blogs, not docs with generated navigation. There's no upside for this project that Astro doesn't also give me.

**Q39. Why not Docusaurus? It's literally built for this exact use case.**

> This is the fairest version of the question, and I'll concede the point partially: Docusaurus does everything this project does, out of the box, today, with versioned docs and i18n on top. If the goal were "have a docs site by Friday", Docusaurus is the correct answer and building this would be a mistake. Two reasons I went the other way. First, it's React all the way down — a docs page that is 99% static text ships and hydrates a React tree, which is exactly the cost Astro exists to remove. Second — and I'll be straight with you — the *point* was to understand file-based routing, build-time file discovery, and static generation from the inside. Adopting Docusaurus would have given me a site and taught me a config file.

**Q40. Static generation vs SSR vs client-side rendering — give me the real tradeoff, not the marketing version.**

> SSG moves all the work to build time. You pay once, per deploy, and every reader gets a file off a CDN edge — fastest possible first paint, no server, no runtime attack surface, no scaling story to write. You pay for it in two currencies: **staleness** — content changes require a rebuild and redeploy, so there's no such thing as "publish instantly from an admin panel" — and **uniformity** — everyone gets identical HTML, so no personalization, no per-user data, no auth-gated content, because the page was rendered before anyone asked for it. SSR reverses it: fresh and personalizable, but you now own a server, its latency, its scaling, and its security. CSR ships a shell and fetches — worst first paint, worst SEO, best for app-like interactivity. Docs are read-only, structured, and identical for every reader, which is exactly the shape SSG is optimal for. It's not that SSG is better; it's that this content class is a perfect fit and most content classes aren't.

**Q41. What does a content change actually cost you?**

> A full rebuild and redeploy. Every markdown edit re-globs the tree, re-derives every route, rebuilds the search index and re-emits every page — because the index is embedded in all of them. There's no incremental path in what I built. On a small site that's seconds. On a large one it's the reason people leave SSG.

**Q42. Why clone the sidebar's `innerHTML` for the mobile menu instead of a proper mobile nav component?**

> Because a second component means a second source of truth for navigation, and they will drift. The mobile overlay reads `sidebar.innerHTML` and injects it into a slide-in panel, so the mobile nav is by construction identical to the desktop one — no shared state layer, no duplicated template. It's the lazy option and I think it's the right one. The honest cost is accessibility: an `innerHTML` clone in a div is not a proper dialog. It has no focus trap, no `role`, no `aria-modal`, and focus can escape behind the overlay. The correct version is a native `<dialog>` or an ARIA-compliant off-canvas component, and that's on my improvements list — I'd call it the highest-priority item on it.

**Q43. Body scroll lock — how?**

> `document.body.style.overflow = 'hidden'` while the overlay is open. Crude, and it has the classic iOS Safari caveat, but it's one line and it does the job for the case I have. [FILL: confirm whether you tested this on iOS Safari]

---

## Section 8 — Hard cross-cutting questions

**Q44. When is this system the WRONG choice? Talk me out of using it.**

> Four disqualifiers, and any one of them is fatal. **Auth** — the site is a folder of public files on a CDN; there is no per-page access control and bolting one on means abandoning the architecture, not extending it. **Anything dynamic or personalized** — the HTML was rendered before the reader existed. **Scale** — every content change is a full rebuild, and my search index is embedded in every page, so bytes grow with pages squared; past a few hundred pages the build gets slow and the pages get fat. **Non-technical authors** — my content model *is* the git repository. If your writers want a WYSIWYG and a Publish button, they want a CMS and I should not talk them out of it.

**Q45. What breaks first as this grows?**

> The search index. It's embedded in every page's HTML, so it's the term that grows fastest, and it degrades quietly — nothing errors, pages just get heavier. Second is build time on every trivial content edit. Third is the two-level sidebar cap, which anyone organising a real docs tree will hit and which fails silently.

**Q46. Where's the test coverage?**

> [FILL: were there any tests? The report documents none. If there were none, say so plainly — "there were no automated tests; it's a learning project and the build itself was the only gate" — and then say what you'd test first: the `fileToRoute` path-to-route conversion and `buildTree`, because they're pure functions with edge cases like `/index` collapsing, and they're exactly where the two routing bugs lived."]

**Q47. What's the security surface?**

> Close to nothing, and that's the strongest argument for the architecture. There's no server to exploit, no database to inject into, no session to hijack, no user input that reaches any backend, because there is no backend. The only code executing anywhere is client-side JS operating on first-party content baked in at build time. The one place I had to think about it at all was the search dropdown writing matched text into `innerHTML`, which is why `escapeHtml()` is there.

**Q48. What would you do differently if you rebuilt it today?**

> Three things, in order. Move to Astro **Content Collections** with a Zod frontmatter schema, so a typo in `title:` fails the build instead of silently degrading — that's a real class of bug the current design cannot catch. Make the sidebar renderer recursive, or at minimum make it fail loudly at build time when the tree exceeds what it can draw. And make the mobile menu a real `<dialog>` — the `innerHTML` clone is clever and inaccessible, and I'd take the boring accessible version.

**Q49. What's the single thing you're least proud of?**

> The two-level sidebar limit failing silently. Everything else in this project either works or fails loudly. That one drops content on the floor and says nothing, which is the exact failure mode a build step exists to prevent.

**Q50. What did you actually learn that transfers?**

> The build-time/runtime split as a design axis. Astro forces you to ask, for every piece of work: does this have to happen while a user is waiting? Almost always the answer is no, and the work moves to the build. That's the same instinct as precomputing, caching, or doing static analysis instead of runtime checks — it's not an Astro idea, Astro just made me hold it explicitly. The second thing is that `import.meta.glob()` is a filesystem-as-data-source pattern that generalises far beyond this — any time content lives in files and needs discovering, that's the shape.

**Q51. What's the future roadmap?**

> The written list: a proper accessible off-canvas mobile menu, deeper sidebar nesting, chunking the search index into a separately-fetched JSON, per-page in-document search as a complement to global search, a GitHub Actions pipeline building and deploying to Cloudflare Pages on push, build-time image optimisation via Astro's pipeline, and — the speculative one — a Capacitor/Tauri wrapper to ship it as a mobile and desktop app. [FILL: the Capacitor/Tauri idea is listed in PROJECT_JOURNEY.md — be ready to say whether you'd actually do it or whether you now think it's scope creep]

---

## Section 9 — Closing

**Q52. Sell me this project in one sentence.**

> It's a documentation site with no backend, no database, no CMS, no routing config, and no frontend framework in the browser — and the reason it's on my resume isn't the code, it's the list of things I decided not to build.

**Q53. Why should I care about a static site generator when I'm hiring an AI engineer?**

> Because the failure mode I see most in AI engineering isn't ignorance, it's over-building — agents with six tools where two would do, retrieval layers over corpora that fit in a prompt, frameworks wrapped around three API calls. The discipline this project demonstrates — identify the actual shape of the problem, pick the minimum architecture that fits it, and be able to say precisely when that architecture stops working — is the same discipline. This one just happens to be small enough that you can see all of it.

---

## Cheat card — trigger → exact line to say

| Interviewer says | You say |
|---|---|
| "Why is this even on your resume?" | "It demonstrates restraint. It's defined by what it refuses to have — no config, no CMS, no database, no framework in the browser. Knowing where to stop is the skill." |
| "Isn't this trivial?" | "It's small. I'm not going to pretend it's more. But every decision in it was made, not defaulted into, and I can tell you when each one breaks." |
| "Why Astro?" | "Zero JS by default, static output, real component model. Next ships React for a page that's text. Hugo wins on build speed at a scale I don't have. Docusaurus would've given me a site and taught me a config file." |
| "How does 'no routing config' work?" | "`import.meta.glob()` enumerates the markdown at build time, `getStaticPaths()` turns each path into a route param, Astro pre-renders one HTML file per route." |
| "Search index in every page — really?" | "Deliberate tradeoff with a known ceiling: no network round-trip, never stale, breaks past ~50 pages. Chunk it into a fetched JSON — that's the documented fix." |
| "Why not a search library?" | "The library is the heavier option at this scale. 80 lines of weighted scoring finds the page. I'd swap to FlexSearch the day the corpus grows or someone wants typo tolerance." |
| "When is this the wrong tool?" | "Auth, personalization, non-technical authors, or thousands of pages. Any one of those and I'd pick something else without arguing." |
| "What's broken?" | "Sidebar caps at two levels and fails silently. That's the one I'm least proud of — it drops content and says nothing." |
| "What would you change?" | "Content Collections with a Zod schema so bad frontmatter fails the build. Recursive sidebar. A real `<dialog>` for the mobile menu." |
| Tries to make you defend it as "big" | Don't take the bait. "It's a small project told honestly. The judgment is the point, not the size." |

---

## Prep priority

**Tier 1 — you will be asked these; know them cold**
1. Why is this on the resume (Q1, Q2) — say it confidently, don't get defensive
2. The "no routing config" mechanism: glob → `getStaticPaths()` → pre-rendered HTML (Q12)
3. Why Astro over Next/Hugo/Jekyll/Docusaurus, one real tradeoff each (Q36–Q39)
4. When this is the wrong tool (Q44)
5. The embedded search index tradeoff and its ceiling (Q26, Q27)

**Tier 2 — likely, and they separate you from a candidate who just used a template**
6. SSG vs SSR vs CSR, the real currencies: staleness and uniformity (Q40)
7. The `[...slug]` string-not-array bug and what it taught you (Q15, Q16)
8. The `scroll-padding-top` / `scroll-margin-top` fix (Q34, Q35)
9. `rootMargin: '-80px 0px -80% 0px'` — defend both numbers (Q33)
10. Why `<details>` instead of a JS accordion (Q18)

**Tier 3 — depth if they dig**
11. `buildTree()` — the four steps (Q17)
12. Search scoring weights 10/5/2 and the 200-char excerpt limitation (Q24, Q28)
13. `escapeHtml()` before `innerHTML` (Q29)
14. Content Collections as the biggest available upgrade (Q9, Q48)
15. Mobile-menu DOM cloning and its accessibility cost (Q42)

---

## [FILL] list — you must supply these before the interview

1. **Q4** — Was it used by anyone besides you? Deployed anywhere publicly? If not, say "learning project, I was the user" and stop.
2. **Q5** — How long did it take to build? The report is dated 2026-06-23 but states no elapsed time.
3. **Q8** — Did you know about Astro Content Collections at the time and choose not to use them, or discover them later? Do not claim a decision you didn't make.
4. **Q30** — Was the 150ms debounce measured/tuned, or a default you picked? Do not claim a benchmark you didn't run.
5. **Q43** — Did you test the body-scroll-lock on iOS Safari?
6. **Q46** — Were there ANY automated tests? The report documents none. If none, say so plainly.
7. **Q51** — The Capacitor/Tauri cross-platform packaging idea is in `PROJECT_JOURNEY.md`. Decide now whether you'd defend it or call it scope creep — an interviewer may well call it scope creep for you.
8. **Page count** — several answers say "under 50 pages" (the report's own figure for what the embedded index is acceptable at). Know the *actual* number of markdown files in your `src/content/docs/`.
9. **Build time** — no build-time number exists anywhere in the source. If asked "how fast is the build?", say you didn't measure it. Do not guess.

---

## Never say these

- Any performance number, benchmark, page-load time, Lighthouse score, or user count. **None exist in the source.** If asked, say you didn't measure it — that is a better answer than a number you can't defend.
- "It scales." It doesn't, past a few hundred pages, and you know why.
- Anything that dresses this up as a big system. The interviewer already knows it isn't. Honesty here protects the credibility of your genuinely large projects.
