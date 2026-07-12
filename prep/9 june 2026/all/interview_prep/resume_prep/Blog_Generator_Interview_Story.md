# Blog / Docs Site Generator — The 3-Minute Spoken Story

**Use when:** "Tell me about the docs site generator." / "Walk me through this one." / any invitation to narrate a smaller project.

**Tone:** Short. Confident. Amused at yourself. This is a story about *judgment*, not complexity. Do not inflate it — the interviewer already knows it's your smallest project, and pretending otherwise will make them re-audit your good ones.

---

## THE STORY

### 1. Setup — the world before

> I wanted to write documentation. That's it. That was the entire requirement.
>
> I had a folder of Markdown files. I wanted them to be a website — with a sidebar, a table of contents, a search box. The kind of thing you've read a hundred times and never thought about.

### 2. The real problem — reframed

> Here's the thing I noticed, and it's the reason this project exists.
>
> Every tool that promises to help you write ends up making you *configure* instead of write. You want to publish a doc, so you pick a CMS — now you're running a backend and a database for content that never changes. You pick a framework — now you're maintaining a routing table, and every new page is an entry in a config file you have to remember to update.
>
> The problem was never rendering Markdown. Rendering Markdown is a solved problem. The problem is that **the distance between "I wrote a paragraph" and "a human can read it" is filled with infrastructure.**

### 3. The obvious build — and why it's a trap

> The obvious move is to reach for the full framework. Docusaurus, or Next.js, or a CMS. And I want to be fair to that move: it *works*. Docusaurus is genuinely excellent at this.
>
> But watch what happens. You now have a `sidebar.js`. You have a routing config. You have a React runtime shipping to the browser to render a page that is, structurally, a paragraph of text and some links. And every one of those things is a surface that can break, that needs updating, that will ask for your attention on a Tuesday when you meant to be writing.
>
> The trap isn't that the framework is bad. The trap is that the framework gives you *things to maintain*, and maintenance always wins the fight for your afternoon.

### 4. The villain

> So let me name the villain properly, because it isn't a bug and it isn't a framework.
>
> **The villain is the tool that quietly becomes the work.**
>
> You sit down to write. Three hours later you are debugging a routing config, you have learned something about YAML, and you have not written a single sentence. And it doesn't feel like failure — it feels like *progress*, because you fixed something. That's what makes it a villain and not just an annoyance.
>
> And here's the cruel part: **every feature you add to a writing tool is a new way to avoid writing.** Configurability isn't neutral. It's an invitation.

### 5. The hero — the design insight

> So I inverted the requirement. Instead of asking "what should this tool have?", I asked "what can it *refuse* to have?"
>
> No backend. No database. No CMS. No routing config. No frontend framework shipped to the browser. No search library.
>
> And the load-bearing decision: **the folder structure IS the navigation, and the file path IS the URL.** Not "the folder structure generates a config that produces the navigation." There is no config. There is no intermediate artifact to fall out of sync, because there is nothing between the filesystem and the site.
>
> That's convention over configuration, taken seriously enough to hurt. You drop `guides/advanced.md` in the folder. It's at `/docs/guides/advanced`. It's in the sidebar. It's in the search index. Nobody told it to be. You wrote a file.
>
> I built it on Astro, because Astro's default is zero JavaScript to the browser — you opt *in* to interactivity, per component, instead of opting out of a runtime you never wanted. That default is the whole reason it's the right tool: it agrees with me about what a docs page is.

### 6. The dip

> And then the framework told me no.
>
> I had one route file — a catch-all, `[...slug].astro` — that was supposed to handle every doc page in existence. That file is the entire embodiment of "no routing config." And the build failed. Flat refusal. Astro will not build a dynamic route in static mode unless you declare, ahead of time, every single valid path it can produce. It wants a manifest.
>
> Which is *exactly the thing I built this to avoid.* I set out to eliminate the routing table, and about ninety minutes in, the framework was demanding a routing table.
>
> And it got worse before it got better, in the stupidest possible way. I wrote the path declaration, and my flat pages worked — `install.md`, `faq.md`, all fine. So I believed it. Then every *nested* page broke. I had assumed the catch-all handed me an array of path segments — `['getting-started', 'install']` — and it doesn't. It hands you one string: the whole remaining path. My flat pages had worked because with one segment, a wrong model and a right model look identical.
>
> So I'd been confidently wrong, and the flat pages had been *reassuring* me I was right.

### 7. The turn

> The realization wasn't clever. It was a distinction I'd been missing.
>
> The function Astro demanded — `getStaticPaths()` — is not configuration. **It's derivation.**
>
> Configuration is a list you write down and then have to keep true. Derivation is a function that reads the world and produces the list. Same output, opposite maintenance story. My `getStaticPaths()` doesn't contain a single route. It globs the content directory, converts each file path to a slug, and hands the list back. It's about six lines and it will *never* need editing again — not when I add a page, not when I add a folder, not ever.
>
> So the framework didn't beat me. It made me say the principle more precisely. "No routing config" doesn't mean *no route list exists* — of course one exists, something has to know what pages there are. It means **no human ever writes or maintains that list.** The build derives it from the filesystem, every time, from scratch.
>
> That distinction — config you maintain versus derivation that maintains itself — is the actual idea in this project.

### 8. The landing

> What came out is a folder of static HTML. It deploys to any CDN — Cloudflare Pages, GitHub Pages, anywhere that serves files. No server. No database. No runtime. Sidebar built from the file tree, search index built at build time and embedded in the page, table of contents with a scroll spy — all of it derived, none of it configured.
>
> And I'll be straight with you about the size of this: it's the smallest thing on my resume. It's a learning project. I'm not going to dress it up.
>
> But I keep it there deliberately, because of the principle it cost me a bad afternoon to learn: **the tool that asks you to maintain it has started competing with the work.** Every config file is a small tax collected forever. The strongest thing this system has isn't a feature — it's the list of features it refuses to have.
>
> And I'd argue that's not a static-site lesson. That's the lesson I most want to be right about in AI engineering, where the default failure mode isn't ignorance — it's building six things when two would have done.

---

## Why this works on this audience

- **It disarms the obvious attack before they land it.** They are *already thinking* "why is this here next to a real system." You say it out loud, first, without flinching. Now they can't use it.
- **The villain is a discipline problem, not a technical one.** Every engineer interviewing you has lost an afternoon to a config file. You are describing their Tuesday.
- **The dip is real and it's documented.** You genuinely got beaten by `getStaticPaths()` and you genuinely had a wrong mental model of rest params that flat routes concealed. Nothing here is manufactured.
- **The turn is a distinction, not a heroic push.** "Config you maintain vs. derivation that maintains itself" is a *portable idea*. Interviewers remember portable ideas and forget features.
- **The landing pivots to AI engineering.** The over-building failure mode is the single most recognisable pathology in the field right now, and you've just spent three minutes demonstrating the antidote on something small enough to fully inspect.

---

## Delivery notes

| Beat | Time | How to play it |
|---|---|---|
| Setup | 0:00–0:15 | Flat, almost bored. "I wanted to write documentation. That was the requirement." Under-sell hard. |
| The real problem | 0:15–0:35 | Lean in. This is where they start nodding. |
| The obvious build | 0:35–0:55 | **Be genuinely fair to Docusaurus.** If you sneer at it you look junior. Concede it works, *then* turn. |
| **THE VILLAIN** | 0:55–1:15 | Slow down. Land "the tool that quietly becomes the work" and then **stop talking for one beat.** |
| The hero | 1:15–1:45 | Pick up pace. The list of refusals should be rattled off like a boast, because it is one. |
| **THE DIP** | 1:45–2:20 | Self-deprecating, not anguished. "And then the framework told me no" — enjoy it. The flat-pages-lied detail is the best line in the story; don't rush it. |
| The turn | 2:20–2:45 | Quiet and precise. This is the one idea you want them to leave with. |
| The landing | 2:45–3:05 | Concede the size **first**, then state the principle. Concede-then-assert. Never the reverse. |

**Hard rules of delivery:**
- **Never defend the project's size.** Concede it instantly and move to the principle. The concession is what makes the principle credible.
- **No numbers.** You have no benchmarks, no page-load times, no user counts. If pushed, "I didn't measure it" is a stronger answer than a number you can't defend.
- If they interrupt at the villain to say "so, Docusaurus?" — **agree first**: "For shipping a docs site by Friday, yes, and I'd tell a team to use it. I wanted to understand the machine, not the config file." Then continue.

---

## Lines to memorize (say these exactly)

1. **"Every tool that promises to help you write ends up making you configure instead of write."**
2. **"The tool that quietly becomes the work."** ← the villain, verbatim
3. **"Every feature you add to a writing tool is a new way to avoid writing."**
4. **"The folder structure IS the navigation. There's no config in between, because there's nothing in between."**
5. **"I set out to eliminate the routing table, and ninety minutes in, the framework was demanding a routing table."**
6. **"My flat pages had worked, which is what made me so confident I was wrong."**
7. **"`getStaticPaths()` isn't configuration. It's derivation. Config is a list you maintain; derivation is a function that reads the world and produces the list."**
8. **"No routing config' doesn't mean no route list exists. It means no human ever writes or maintains it."**
9. **"The strongest thing this system has isn't a feature. It's the list of features it refuses to have."**
10. **"It's the smallest thing on my resume, and I keep it there on purpose."**

---

## [FILL] list — supply before you tell this story

1. **"about ninety minutes in"** (Beat 6) — the source does not record how long you'd been building when `getStaticPaths()` failed. `[FILL: replace with a true duration, or cut the time reference entirely and just say "and then the framework told me no"]`
2. **"a bad afternoon"** (Beat 8) — `[FILL: confirm the routing bugs cost you roughly an afternoon; if you don't remember, cut the time and say "a principle I only learned by getting it wrong"]`
3. **"Three hours later you're debugging a routing config"** (Beat 4) — this is stated as a general truth about tools, not a claim about you, so it's safe as written. But if you want to make it personal, `[FILL: confirm this actually happened to you with a specific tool, and name it]`
4. **Deployment** — the story says the output "deploys to any CDN," which the source supports as a *capability*. It does not say you deployed it. `[FILL: did you actually deploy it anywhere? If not, keep the wording as capability — "it deploys to" — and never upgrade it to "it's deployed at"]`
5. **The Docusaurus concession** — `[FILL: optional, strong if true — have you actually used Docusaurus? If yes, say so; a concession from experience lands ten times harder than a concession from reading]`

---

## What is NOT in this story, and must not be added

- Any performance metric, build time, Lighthouse score, page count, or user count. **The source contains none.** Inventing one here would be the single fastest way to make an interviewer re-audit every number on your resume.
- Any claim that this project was used in production, by a team, or by anyone but you.
- Any framing that makes this sound larger than it is. **The honesty is the load-bearing element of this story.** A small project told straight is impressive. A small project inflated is fatal — and it takes your agent runtime down with it.
