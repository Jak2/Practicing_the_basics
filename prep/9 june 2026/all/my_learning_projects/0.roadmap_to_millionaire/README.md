# Roadmap to Millionaire — Viral Trend Engine

**Owner:** Jaya Arun Kumar Tulluri
**Started:** 2026-07-02
**Status:** Brainstorming / research phase

## The Original Idea (Jaya's prompt, 2026-07-02)

> Build an AI agent that captures all the trending viral content — a list of 100 points
> of everything going viral on the internet. Goal: earn a million in the shortest
> reasonable time. Have social media accounts to publish on; platforms like Instagram
> pay for views. Inspired by Ryan Reynolds' ad agency "Maximum Effort". Research social
> media algorithms and create an HTML file for each platform. As many platforms as
> possible.

**Refinements agreed after discussion:**
- Not reposting raw viral content (demonetization risk). Instead: **our own explanation /
  commentary / ads on top of viral trends**, eventually delivered by an **AI character**.
- **One persona across multiple platforms** — not a fleet of accounts.
- Build BOTH tracks: **Creator fuel** (trend radar feeding our own content) and
  **Trend intelligence product** (sellable Top-100 viral report).
- Build or adopt a cross-posting tool (ContentPilot-like) to publish everywhere.

## Research Findings (2026-07-02)

### People already doing this (proof the model works)
- **Daily Dose of Internet** — curates viral clips WITH original narration/commentary:
  ~$138K–$388K/month ad revenue. This is the closest existing model to our idea.
- **Fern** (faceless explainer channel): ~$80K/month.
- **DaFuq Boom** (AI-driven faceless): $500K–$1.3M/month at the extreme top.
- Faceless channels = 38% of new creator monetization ventures; production cost has
  collapsed to <$3/video with AI voice + auto-assembly.
- **AI characters/virtual influencers:** Lil Miquela (~$11M career brand revenue),
  Lu do Magalu (~$2.5M/yr). Brand deals $2K–$15K/post at 100K+ followers. 74% of
  consumers accept AI creators if transparent. **FTC requires double disclosure**
  (sponsorship + AI persona) — fines up to ~$51K/violation.
- **Trend intelligence side:** Exploding Topics does **$3.2M ARR** at $39–$250/month
  subscriptions — validates the Top-100 report as a product.

### Monetization gates (2026) and how to pass them fastest
| Platform | Gate | Fastest path |
|---|---|---|
| YouTube | Fan funding at 500 subs + 3 videos + 3K watch hrs (or 3M Shorts views); full ads at 1K subs + 4K hrs / 10M Shorts views in 90 days | Shorts — one viral short can cross the line |
| TikTok | Creator Rewards: 10K followers + 100K views/30 days; LIVE gifts at just 1K followers. Pays $0.40–$1.00 per 1K views | 21–34s videos, strong hooks, >1min videos for Rewards |
| Instagram | Subscriptions/badges at 10K followers; Reels gifts lower | Reels riding trending audio |
| Any platform, day one | None | Affiliate links + (later) brand deals — no threshold |

**Key insight:** ad revenue is only 30–50% of successful channels' income. Affiliates,
sponsorships, and digital products (our trend report!) work before any gate is passed.

### Cross-posting tools (buy vs build)
- **Buffer** — $5/channel/month, supports IG/TikTok/YT/X/Threads/Pinterest/Bluesky. Cheapest start.
- **Publer** — $12/month, bulk CSV scheduling (good for automation pipelines).
- **PostEverywhere** — $29/month, per-platform AI tone variants + autonomous agents.
- Verdict: **don't build ContentPilot-v2 yet** — pipe our agent's output into Buffer/Publer
  via their APIs first; build our own poster only if the tools limit us.

## The Two Tracks

1. **Creator fuel:** daily agent sweep (Google Trends, YouTube trending, Reddit, TikTok
   Creative Center, X trends, Know Your Meme) → ranked Top-100 viral list → per-platform
   HTML briefing pages tuned to each algorithm → we make original commentary content
   (later fronted by our AI character) → publish via scheduler.
2. **Trend intel product:** the same Top-100, polished into a daily/weekly report that
   can be sold (newsletter → dashboard), Exploding Topics-style.

## Persona & Niche Decision (2026-07-02)

Jaya selected a combination of:
- **Niche trend explainer** — niches of interest: **tech/AI trends** and **India-focused viral trends**
- **Trend analyst character** — a persona whose identity is "I read the data and tell you
  what's blowing up before it peaks" (synergizes with the trend-intel product)

Working direction (Claude's recommendation, pending Jaya's confirmation):
**"The AI trend analyst who spots what's blowing up — with a special eye on India."**
Tech/AI as the primary niche (highest CPM, best brand-deal rates, and we can credibly
show our own AI pipeline as proof of expertise), with India-focused trends as a
recurring segment/lens rather than a second separate niche — one persona must feel
coherent, and "AI + India's internet" is a huge, underserved intersection (India is the
largest audience pool on IG/YT, but most AI-trend content is US-centric).

## Platform Strategy (decided 2026-07-02)

**Primary home base: YouTube Shorts** — lowest monetization bar (fan funding at 500 subs;
full ads at 1K subs / 10M Shorts views), best long-term ad RPM for tech/AI content,
content ages well and doubles as search-discoverable assets. Other platforms receive
cross-posts with platform-tuned variants.

Platform roles:
| Platform | Role | Payout reality |
|---|---|---|
| YouTube | HOME BASE — grow + earn | Shorts ~$0.05–$0.10/1K; long-form tech RPM $10–$30 |
| Instagram | India reach + brand deals | No open ad share; deals/affiliates only |
| TikTok | Global/US audience (banned in India) | $0.40–$1.00/1K via Creator Rewards; LIVE gifts at 1K followers |
| X | AI-community authority + report funnel | ~$0.01–$0.03/1K — negligible; distribution value |
| Facebook | Passive cross-post bonus | Reels $0.02–$0.20/1K; long-form $1–$5/1K |

## Reference Files (in this folder)

- `glossary.html` — social-media-marketing terms (ARR, CPM, RPM, CTR, ROAS, CAC, LTV…)
- `platforms/youtube.html` — algorithm, monetization gates, reward policy (home base)
- `platforms/instagram.html` — ranking signals (watch time, sends/reach), programs
- `platforms/tiktok.html` — FYP batch testing, Creator Rewards, India-ban note
- `platforms/x-twitter.html` — open-source ranking weights, ad-share reality
- `platforms/facebook.html` — Content Monetization Program, cross-post role
- `trend-engine-design.md` — approved architecture design for the daily Top-100 trend agent
- `architecture-classification.html` — is it RAG / multi-agent / pipeline? (visual explainer)
- `trend-engine-plan.md` — phased TDD implementation plan (6 tasks: store → scorer →
  collectors → enricher → publisher → orchestrator)

## Architecture Classification (2026-07-02)

Jaya asked what category the trend-engine falls under. Answer, detailed in
`architecture-classification.html` with pipeline diagram, z-score bar chart, and dedup funnel:

**It is an LLM-augmented data pipeline (agentic ETL) — not RAG, not multi-agent.**
- **Not RAG:** no retrieval-then-generate loop; the enricher only sees today's freshly
  scored candidates, nothing pulled by similarity search from stored history. (RAG-shaped
  retrieval *does* arrive later, in the phase 2–3 mem0 persona layer — "have we covered
  something like this before?" — but that's outside the trend-engine core.)
- **Not multi-agent:** only one of five pipeline stages touches an LLM at all (the
  enricher), and it's a single structured batch call, not an autonomous multi-turn actor
  coordinating with others. Collectors/store/scorer/publisher are plain deterministic code.
- **Is an LLM-augmented pipeline:** standard Extract→Transform→Load shape; the LLM is used
  only where language judgment is genuinely needed (deduping near-duplicate stories,
  writing the "why it's viral" line) — everything else (z-score, decay, corroboration
  scoring) is deterministic, reproducible, and cheap by design.
- **Where it could become agentic later:** a future "decide which topics to actually
  script videos for" step — weighing past coverage (via mem0 retrieval), what explanation
  styles performed best, and upload cadence — is a genuine multi-step judgment call and a
  legitimate candidate for a real agent. Not needed for the MVP.

## Honest constraints (keep ourselves accountable)
- $1M is a multi-year outcome for >99% of creators; top earners above are outliers.
- Reposted/unmodified content gets demonetized; **transformation (commentary) is the moat**.
- AI persona brand deals require FTC double disclosure.
- Platform APIs (esp. Instagram/TikTok posting) have approval hoops — schedulers solve this.

## Activity Log
- **2026-07-02** — Idea captured, refined (commentary model, single persona, both tracks).
  Web research on comparable earners, monetization gates, cross-posting tools. This file created.
  Next: pick niche/persona angle, then design the trend-capture agent + per-platform HTML pages.
- **2026-07-02** — Persona decided: trend-analyst character in the tech/AI niche with an
  India-focused lens (options 2+3 combined). Next: design the trend-capture agent,
  data sources, and per-platform HTML briefing pages.
- **2026-07-02** — YouTube Shorts chosen as primary platform. Created `glossary.html`
  (marketing terms) and per-platform briefs in `platforms/` covering algorithm mechanics,
  monetization eligibility, and reward policies for YouTube, Instagram, TikTok, X, Facebook.
  Next: design the trend-capture agent (data sources, Top-100 ranking, output pipeline).
- **2026-07-02** — Trend-agent design session: selected candidate data sources (Reddit,
  YouTube Data API, Hacker News, Google Trends, Wikipedia pageviews, TikTok Creative
  Center, GitHub trending, X trends) and scoring approach (z-score spike detection +
  time-decay ranking + cross-source corroboration). Three architectures proposed
  (pure-script / pure-agent / hybrid); awaiting Jaya's pick.
- **2026-07-02** — Jaya approved approach C (hybrid: Python collectors + SQLite +
  statistical scorer + one Haiku enrichment pass + HTML/JSON publisher). Full design
  written to `trend-engine-design.md` — covers collectors (Reddit/YouTube/HN/Wikipedia
  in MVP), scoring formula, dedup/enrichment, per-platform output briefs, error handling,
  testing, success criteria. Awaiting design review before implementation planning.
- **2026-07-02** — Direction crosscheck vs original idea: PASS (see "Crosscheck" section).
  Memory-library research done: SQLite stays as the trend-engine's data store (metrics
  are time-series, not agent memories); **mem0** (OSS, ~48K stars, vector+graph+KV,
  free tier) selected as the phase-2/3 memory layer for the persona & content side
  (what we've covered, how explanations performed, audience feedback). Zep/Graphiti
  noted as alternative if temporal knowledge-graph needs grow (63.8% vs 49.0% on
  LongMemEval but far heavier token footprint); Letta rejected (full agent runtime,
  overkill). MemPalace stays for Jaya's personal workspace memory, not the product.
- **2026-07-02** — Data-kinds explainer + storage sequencing added (see "Data & Memory
  Stack"). Confirmed mem0 runs free/local (Apache-2.0). Jaya suggested cloud DB;
  decision: local SQLite for MVP → Supabase free tier (Postgres + pgvector) when the
  engine needs to run in the cloud; Firebase rejected as poor fit.
- **2026-07-02** — Classified the architecture (Jaya's question): LLM-augmented data
  pipeline / agentic ETL, not RAG, not multi-agent. Wrote `architecture-classification.html`
  with pipeline diagram, z-score bar chart, and dedup funnel visuals; see
  "Architecture Classification" section above for the summary.
- **2026-07-02** — Session resumed; design treated as approved. Wrote full TDD
  implementation plan (`trend-engine-plan.md`): Task 1 scaffold+SQLite store, Task 2
  scorer, Task 3 four collectors, Task 4 enricher (Haiku, degraded mode), Task 5
  publisher (top100.html/json + platform briefs), Task 6 orchestrator + e2e. Code will
  live in `trend_engine/` with its own git repo. Awaiting execution-mode choice.
- **2026-07-02** — **TREND ENGINE BUILT AND WORKING.** All 6 tasks implemented via
  subagent-driven development (fresh implementer + reviewer per task, fix cycles on
  findings), final whole-branch review passed after fixes. Code at
  `my_learning_projects/trend_engine/` (14 commits, 43 tests green). First live run:
  1,081 items collected (HN 60 + Reddit 25 + Wikipedia 996) in 49s, Top-100 published
  to `output/2026-07-02/` — in degraded (math-only) mode since API keys not yet set.
  Notable build learnings: Reddit blocks unauthenticated JSON (switched to Atom RSS with
  rank-proxy engagement + 10s pacing); Wikimedia requires a descriptive User-Agent;
  reviewers caught real bugs (keyword substring false-positives, LLM-cluster
  double-counting, javascript: URL injection, cold-start ranking flatness) — all fixed.
  **Pending on Jaya:** set YOUTUBE_API_KEY and ANTHROPIC_API_KEY (steps given earlier),
  then run `python3 run_daily.py` from `my_learning_projects/trend_engine/` for the
  first fully-enriched report. Next phase options: daily cron scheduling, YouTube
  category filtering, content-age decay, Google Trends collector.
- **2026-07-02** — Added two scope-control knobs to `trend_engine/config.py`:
  `EXCLUDE_KEYWORDS` (hard filter, drops matching topics before scoring — sports/
  obituaries/celebrity noise by default) and `SOURCE_ENABLED` (per-collector on/off
  toggle). Also left a commented-out third-niche-category example (config +
  score.py) for adding e.g. finance/crypto later. Confirmed: no scheduling loop
  exists — `run_daily.py` is single-pass; scheduling is external.
  Added `trend_engine/run_cron.sh` wrapper + documented crontab entry (cron doesn't
  inherit shell env vars, so keys load from a gitignored `.env.cron`). Wrote
  `trend_engine/README.md` as the full operator manual (quick start, API key setup,
  config reference, output guide, cron setup, troubleshooting). 46/46 tests green,
  commit `9d97bd2`.
- **2026-07-02** — Readiness check: engine runs end-to-end but needs
  `ANTHROPIC_API_KEY` set (else permanently degraded), Reddit is rate-limit-fragile on
  this network, and content-age decay / YouTube category filtering / Wikipedia noise
  are known rough edges (not blockers). Built a **local web dashboard**
  (`trend_engine/ui/`, stdlib-only, `python3 ui/server.py` → localhost:8765): pipeline
  diagram that lights up per stage, one-click Launch button, environment-key checklist,
  live log tail, run history table, link straight to the finished report, and an
  in-page "how to use this" walkthrough. Verified all endpoints (status/log/launch)
  live. Commit `860bf95`.
- **2026-07-02** — Switched API key setup to a `.env` file (stdlib-only loader in
  `trend_engine/env_loader.py`, no new dependency) — no more `export` needed; a
  `.env.example` template is committed. Dashboard's pipeline stages are now foldable
  panels showing what each stage does under the hood + a live status note while
  running; "How to use this" became a numbered foldable accordion. README expanded
  with a full "Problems you're likely to run into" section (cold-start ranking,
  Reddit rate limits, degraded-but-green runs, off-niche noise, per-run LLM cost,
  env-reload gotchas, orphaned subprocess risk). 49/49 tests green, commit `1f57ba8`.
- **2026-07-05** — Full crosscheck pass (`/goal` directive): re-read every module
  against the design spec and the final whole-branch review's deferred findings. Fixed
  two real Important-severity gaps that were still open: (1) **content-age decay was a
  near-no-op** — recency scoring used collection time, not the post's real creation
  time, since every topic in a run gets fetched within the same few minutes. Added a
  nullable `content_created_at` column (auto-migrates existing DBs, no manual reset
  needed) populated from real source timestamps — HN `time`, Reddit `<updated>`,
  YouTube `publishedAt` — with Wikipedia falling back to fetch time (it has no natural
  per-article creation timestamp). Verified live: 94 distinct age values in a real run
  vs near-constant before. (2) **YouTube pulled every trending category** — added
  `YOUTUBE_CATEGORY_IDS` config filter (defaults to Science&Tech + Entertainment) to
  cut music/sports noise. Also fixed a shadowed loop variable in `reddit.py` (cosmetic,
  no functional bug, just confusing to read). Verified via fresh dry run end-to-end
  (exit 0, 1,107 items, degraded mode as expected with no keys set), a dashboard smoke
  test, and a new migration test proving old databases upgrade cleanly. 54/54 tests
  green, commit `963b641`. Remaining known deviation, left as-is: Wikipedia still pulls
  the global top-pageviews list rather than the original design's "crossover
  confirmation" mode — changing that would reduce candidate diversity and wasn't asked
  for; documented as an accepted MVP tradeoff.

## Data & Memory Stack (decided 2026-07-02)

**Kinds of data in this project and where each lives:**
| Kind | Meaning | In our project |
|---|---|---|
| Time-series metrics | Numbers + timestamps; the sequence IS the signal | View counts/upvotes per topic per day (z-scores need exact history) → SQLite |
| Relational | Fixed-shape linked records | Topics, sources, daily Top-100 → SQLite |
| Documents | Free text/HTML | Titles, reports, scripts → files/DB text |
| Vectors | Similarity-searchable meaning | "Covered something like this before?" → mem0 (phase 2–3) |
| Key-value | Simple lookups | Config, quotas, run state |
| Graph | Entities + relations | Zep/Graphiti territory — not needed yet |

**mem0 licensing:** open source (Apache-2.0), `pip install mem0ai`, fully local, no
subscription. Needs a local vector store (embedded default / Chroma / Qdrant) + LLM key
for extraction (~pennies with Haiku). The $249/mo tier is only their hosted cloud.

**Storage sequencing (zero-burden plan):**
1. MVP: local SQLite only — no signups, nothing to maintain.
2. Storage module written as a thin interface (swappable backend).
3. When cloud is needed: **Supabase free tier** (Postgres for metrics + built-in
   pgvector as mem0's vector store — one free service covers both layers).
   Alternatives noted: Turso (hosted SQLite), Qdrant Cloud free 1GB (vectors only).
   Firebase rejected: document model fights time-series aggregation, weak vector search.

## Crosscheck — Original Idea vs Current Design (2026-07-02)

| Original prompt element | Status in design |
|---|---|
| Agent capturing all trending viral content | ✅ Collectors + scorer (Reddit/YouTube/HN/Wikipedia MVP, more in phase 2) |
| "List 100 points" of everything viral | ✅ Daily Top-100 with dedup + ranking |
| HTML file per social platform | ✅ `briefs/<platform>.html` outputs + platform study briefs in `platforms/` |
| As many platforms as possible | ⚠️ Deliberately scoped to 5 (YT home base) — quality over sprawl |
| Get paid for views (algorithms) | ✅ Refined: commentary model passes originality policies; payout table per platform |
| Maximum Effort inspiration | ✅ Refined: original creative on trends, not raw reposting |
| AI character explaining trends | ✅ In roadmap, phase 3 (out of MVP scope by design) |
| Posting tool like ContentPilot | ⚠️ Deferred: use Publer/Buffer APIs first; `top100.json` is poster-ready |
| Creator fuel + trend intel product | ✅ Same engine feeds both; daily archive builds the sellable dataset |

Verdict: on track. The two ⚠️ items are conscious scope decisions, not drift.

## Sources
- https://autofaceless.ai/blog/faceless-content-creator-statistics-2026
- https://awisee.com/blog/successful-faceless-youtube-channels/
- https://www.semrush.com/kb/1490-exploding-topics
- https://milx.app/en/trends/youtube-monetization-requirements-for-2026
- https://flowshorts.app/blog/tiktok-monetization-requirements
- https://www.joinmavely.com/blog/your-guide-to-social-media-network-monetization-requirements/
- https://posteverywhere.ai/blog/best-cross-posting-tools
- https://sproutsocial.com/insights/social-media-scheduling-tools/
- https://communipass.com/blog/ai-influencer-monetization-strategies-2026/
- https://blog.rm11.com/how-to-monetize-an-ai-influencer/
