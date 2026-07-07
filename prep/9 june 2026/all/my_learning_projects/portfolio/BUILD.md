# How This Portfolio Was Built

A full record of the thought process, design decisions, and prompts behind this site.

---

## The Prompts (in order)

### Prompt 1 — First attempt (abandoned)
> *"I want an ultra premium modern elegant neo brutalism based website with curved borders, the website should be clean playful with matte colors but it should not lose its elegance… A modern, markdown documentation site built with Astro and Tailwind CSS. I will write the website content in Markdown, and the headings, subheadings become the sidebar components for navigation. The code should find out the headings and subheadings automatically and add them to sidenav bar as foldable items for navigation with smooth scroll. The UI should have 4 aesthetics with matte colors, it should have two sections left side nav bar and main section for content, rounded borders, dark mode switch, retro font style."*

This built an Astro + Tailwind CSS site with a sidebar-driven markdown doc layout. It worked but the sidebar approach felt more like a documentation site than a personal portfolio.

### Prompt 2 — The current site
> *"Remove all the code, rewrite the entire code with html css tailwind using glassmorphism, neumorphism wherever felt good, remove astro if necessary, use rounded borders, cards, shadows, centered top nav bar with shadows, use the content from the resume."*

This is the site you see now.

---

## Thought Process

### 1. Choosing the stack

The first question was whether to keep Astro or go pure HTML.

**Astro** gave us: markdown parsing, component reuse, hot reload, tree-shaken CSS.
**Pure HTML + Tailwind CDN** gave us: zero build step, open-in-browser simplicity, deployable by dragging a single file to Netlify.

For a single-page personal portfolio that changes rarely, the build pipeline adds complexity without much return. A 45 KB self-contained HTML file that works offline, deploys anywhere, and needs no `npm install` is the right call. Astro was removed.

---

### 2. Choosing the visual language

The brief said **glassmorphism + neumorphism**. These two effects have a tension:

- **Glassmorphism** needs a dark, colorful background to show the frosted-glass depth. The blur + transparency only reads well against a rich, layered backdrop.
- **Neumorphism** needs a consistent mid-tone surface to create the soft raised/inset shadow illusion. It reads poorly on very dark or very light surfaces.

**Resolution:** Use glassmorphism as the primary layer system (cards, navbar, overlays) and neumorphism as a micro-detail treatment for small elements only — skill tags and badge chips where the shadow scale is small enough to work on a dark surface (`#0d1225`).

---

### 3. Background design

A flat dark background kills glassmorphism — there's nothing for the blur to distort. The background needed depth and color.

**Solution — 3 layers:**
1. Base color: `#070b16` (deep navy, not pure black — pure black feels dead)
2. Three `radial-gradient` blobs: violet top-right, cyan bottom-left, indigo center — each at 14–22% opacity
3. A dot-grid overlay via `background-image: radial-gradient(dot 1px, transparent 1px)` at 45% opacity on a 28px grid — adds texture without noise

Additionally, three animated CSS orbs (`position: fixed`, `filter: blur(60px)`, `animation: orbFloat`) give the background a slow, breathing quality that makes the glass cards feel alive.

---

### 4. Color system

| Role | Value | Usage |
|---|---|---|
| Background | `#070b16` | Page base |
| Surface dark | `#0d1225` | Neumorphic tag background |
| Glass card | `rgba(255,255,255,0.038)` | Section cards |
| Glass nav | `rgba(7,11,22,0.72)` | Navbar |
| Accent violet | `#8b5cf6` / `#7c3aed` | Primary accent, timeline dots, borders |
| Accent sky | `#38bdf8` / `#22d3ee` | Secondary accent, alternating tags |
| Text primary | `#f1f5f9` | Body copy |
| Text muted | `rgba(255,255,255,0.50)` | Secondary text, descriptions |

Two accent colors (violet + sky/cyan) allowed the content to be visually segmented — violet for AI/LLM topics, sky-blue for infrastructure/backend topics — without it feeling arbitrary.

---

### 5. Layout structure

```
Fixed glass navbar (centered, max-w-4xl)
│
├── Hero        full viewport height, centered, gradient name, stats row
├── About       single wide glass card, contact info
├── Skills      2×2 grid of glass cards, neumorphic tags inside
├── Experience  left-border timeline, glass card per company
├── Projects    3-column grid of glass cards
├── Education   2-column grid
└── Footer      minimal, 1 line
```

**Navbar design decision:** The navbar is `position: fixed` but not full-width. It sits inside a centered `max-w-4xl` container with `glass-nav` class (blur + border + shadow). This gives the modern "floating pill" look rather than a bar that bleeds edge to edge. The box-shadow has two layers: a deep outer shadow for lift, and a subtle inner `inset 0 1px 0 rgba(255,255,255,0.06)` for a glass edge highlight.

---

### 6. Glass card implementation

```css
.glass-card {
  background: rgba(255, 255, 255, 0.038);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);       /* Safari */
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.5rem;
  transition: background 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.065);    /* slightly more opaque on hover */
  border-color: rgba(139, 92, 246, 0.38);    /* violet border appears */
  box-shadow: 0 12px 40px rgba(109,40,217,0.2), 0 0 0 1px rgba(139,92,246,0.15);
  transform: translateY(-3px);               /* lift */
}
```

The key numbers:
- `0.038` background opacity — low enough to see the backdrop blur but not invisible
- `blur(20px)` — the minimum to feel like glass; less than 16px reads as smudge
- `1px solid rgba(255,255,255,0.08)` — a barely-visible edge highlight that defines the card shape
- On hover: the border shifts to violet at 38% opacity, creating a glow-border effect without a CSS gradient trick

---

### 7. Neumorphism tag implementation

Neumorphism on dark requires two shadows that straddle the surface color:

```css
.neu-tag {
  background: #0d1225;
  /* darker shadow going bottom-right (away from light source) */
  /* lighter shadow going top-left (toward light source) */
  box-shadow: 3px 3px 7px #060a16, -3px -3px 7px #141a34;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.neu-tag:hover {
  /* flip to inset = pressed state */
  box-shadow: inset 2px 2px 5px #060a16, inset -2px -2px 5px #141a34;
}
```

Surface: `#0d1225`
Dark shadow: `#060a16` (surface darkened ~40%)
Light shadow: `#141a34` (surface lightened ~40%)

The `3px` offset and `7px` blur are deliberately small — neumorphism breaks down at large scale on dark surfaces. At tag size (small, pill-shaped), it works.

---

### 8. Typography

Single font family: **Inter** (Google Fonts)
Weights used: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold), 800 (extrabold), 900 (black)

**Monospace:** JetBrains Mono — used only for tags/badges, the logo `JAK.T`, dates, and the footer caption.

**Hero name treatment:** Animated gradient using `background-size: 300% 300%` + `animation: gradShift` — the gradient shifts position continuously giving a slow color-flow effect without any JavaScript.

```css
.name-animated {
  background: linear-gradient(135deg, #c4b5fd, #60a5fa, #38bdf8, #a78bfa);
  background-size: 300% 300%;
  animation: gradShift 6s ease infinite;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

### 9. Animations

Three layers of animation, each with a different purpose:

| Animation | Trigger | Technique | Purpose |
|---|---|---|---|
| Background orbs | Always | CSS `@keyframes orbFloat` + `animation` | Ambient depth |
| Scroll reveal | On scroll into view | `IntersectionObserver` adds `.visible` class | Section entrance |
| Hero gradient | Always | CSS `@keyframes gradShift` | Name visual interest |

**Scroll reveal approach:**
Elements get `opacity: 0; transform: translateY(22px)` by default via the `.reveal` class. An `IntersectionObserver` with `threshold: 0.08` adds `.visible` which transitions both properties. Cards use `transition-delay` via inline `style` attributes to stagger sibling reveals.

No JavaScript animation libraries — everything is CSS transitions triggered by class toggling.

---

### 10. Content structure decisions

The resume had a lot of nested information (4 companies, 3 projects inside Nokia Networks alone). Rather than flattening it, the experience section uses **sub-blocks** — left-bordered `div`s inside the main glass card:

```css
.sub-block {
  border-left: 2px solid rgba(139, 92, 246, 0.28);
  padding-left: 1rem;
}
.sub-block-cyan {
  border-left-color: rgba(6, 182, 212, 0.28);
}
```

Alternating violet/cyan left-borders let the eye quickly distinguish sub-projects within a company without needing a new card per project.

---

### 11. Theme Switcher (Light / Dark)

Though the original design was strictly dark-mode with hard-coded `rgba` values, a DOM-level CSS override for `.theme-light` was implemented. This injects white backgrounds (`#f8fafc`) and recalculates the transparency values for the `.glass-card` elements to ensure the UI remains premium in both color schemes, without requiring a complete rewrite of the Tailwind utility classes.

---

### 12. Dynamic Markdown Fetching

To maintain an easy editing experience for current activities while keeping the single-file structure, a lightweight `<dialog>` modal was added. When opened, it uses the browser's native `fetch()` API to load `MyCurrentActivities.md` and a CDN script (`marked.js`) to render it. This avoids bloating the HTML and allows updating recent activities simply by saving a markdown file in the root directory.

---

## File Structure (final)

```
portfolio/
├── index.html      ← the entire website, self-contained
├── package.json    ← optional: `npm run dev` runs `npx serve .`
├── README.md
└── BUILD.md        ← this file
```

No `node_modules`. No build step. No bundler. One file.

---

## How to run

**Option A — Open directly:**
Double-click `index.html` in your file explorer. Works offline. *(Note: The "My current activities" modal will fail to load its markdown file in this mode due to browser CORS policies on the `file://` protocol).*

**Option B — Local dev server (for live reload with VS Code):**
Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension → right-click `index.html` → Open with Live Server.

**Option C — npm serve:**
```bash
npm run dev     # http://localhost:3000
```

## How to deploy

**Netlify:** Drag the `portfolio/` folder into [app.netlify.com/drop](https://app.netlify.com/drop).
**GitHub Pages:** Push to a repo → Settings → Pages → Deploy from branch → root `/`.
**Vercel:** Import repo → Framework: Other → Output directory: `.` → Deploy.

---

## What to edit

All content lives in `index.html`. Search for the section you want:

| Section | Search for |
|---|---|
| Hero name / title | `id="hero"` |
| About paragraph | `id="about"` |
| Skill tags | `id="skills"` |
| Job entries | `id="experience"` |
| Project cards | `id="projects"` |
| Education | `id="education"` |
| Colors / theme | `<style>` block, CSS variables at the top |
| Fonts | `@import url(...)` line and `font-family` in tailwind config |
