# Trend Engine — Design Doc

**Date:** 2026-07-02 · **Status:** Approved approach C (hybrid) — detailed design for review
**Goal:** Daily agent that produces a ranked Top-100 list of what's going viral (tech/AI global + India lens), enriched with explanations, feeding (1) our content scripts and (2) the sellable trend report.

## Architecture Overview

```
[Collectors]  →  [SQLite store]  →  [Scorer]  →  [Enricher (LLM)]  →  [Publisher]
 reddit.py        trends.db         score.py     enrich.py            publish.py
 youtube.py       (raw counts +     z-score      dedup clusters       top100.html
 hackernews.py     7-day history)   decay        "why viral" lines    top100.json
 wikipedia.py                       corroborate  platform-fit tags    per-platform briefs
```

One command runs the whole daily flow: `python run_daily.py`

## Components

### 1. Collectors (`collectors/`)
Each collector is independent, fetches one source, and writes normalized rows. A source failing must not break the run (log + continue).

| Collector | Source | What it captures | Auth |
|---|---|---|---|
| `reddit.py` | Reddit JSON API | Top/rising posts from configured subreddits (AI, tech, India); score, comments, age | none (public JSON) |
| `youtube.py` | YouTube Data API v3 | Trending videos for regions US + IN, categories Tech/Entertainment; views, likes | free API key |
| `hackernews.py` | HN Firebase API | Top + best stories; points, comments, age | none |
| `wikipedia.py` | Wikimedia pageviews API | Daily pageviews for topics already in our DB (crossover confirmation) | none |

Phase 2 (after MVP works): `tiktok_cc.py` (Creative Center scrape), `github.py` (trending repos), Google Trends (when API access lands).

Normalized row: `(topic_key, source, title, url, engagement, engagement_type, region, fetched_at)`

### 2. Store (`trends.db`, SQLite)
- `raw_items` — every fetched item, append-only.
- `topics` — canonical topics with rolling stats (7-day mean/stddev of mentions & engagement). Topic keys start as normalized title n-grams; the enricher later merges same-story topics.
- `daily_top100` — each day's final ranked output (our historical archive = future product moat).

### 3. Scorer (`score.py`) — pure math, no LLM
For each candidate topic today:
1. **Spike (z-score):** `z = (engagement_today − mean_7d) / max(stddev_7d, ε)`. New topics with no history get a cold-start percentile score against today's population instead.
2. **Freshness (HN decay):** `decay = 1 / (age_hours + 2)^1.8`, normalized 0–1.
3. **Corroboration:** multiplier 1.0 / 1.5 / 2.0 for 1 / 2 / 3+ independent sources.
4. **Niche weight:** ×1.5 if matches AI/tech keyword set, ×1.3 if India-region signal, stackable.

`rank_score = z_norm × (0.5 + 0.5·decay) × corroboration × niche_weight`

Output: top ~150 candidates (extra headroom for dedup shrinkage) to the enricher.

### 4. Enricher (`enrich.py`) — one Claude Haiku call batch
Input: 150 scored candidates (title, source links, engagement numbers).
Tasks in a single structured prompt:
- **Dedup:** cluster items that are the same story; keep highest-scored as canonical, sum cluster scores.
- **Explain:** one-line "why this is viral" per topic (the analyst voice seed).
- **Tag:** `platform_fit` (short-video / thread / long-form), `category` (AI, tech, India, meme, other), `stage` (early-signal / rising / peaking).
Output: validated JSON, final Top 100. On LLM failure: publish un-enriched math-only rankings (degraded mode) rather than nothing.

### 5. Publisher (`publish.py`)
- `output/YYYY-MM-DD/top100.html` — the flagship daily report (dark theme matching our platform briefs).
- `top100.json` — machine-readable, for the future posting pipeline / Publer CSV.
- `briefs/youtube.html`, `briefs/instagram.html`, `briefs/x.html` — per-platform pages listing only topics tagged fit for that platform, with format hints (e.g., "Shorts: hook angle…"). This fulfills the original "HTML file per platform" idea.

## Daily Flow
1. `run_daily.py` (cron or manual): collectors → store → scorer → enricher → publisher.
2. Runtime target: < 5 min; LLM cost target: < $0.05/day (one Haiku batch).
3. Log summary appended to `output/run_log.md`.

## Error Handling
- Per-collector try/except: failed source logged, run continues with remaining sources.
- Rate limits: respect per-API limits; YouTube quota budgeted (~2K units/run of 10K free).
- LLM output validated against JSON schema; one retry, then degraded mode.
- DB is append-only for raw data — a bad run never corrupts history.

## Testing
- Unit tests for the scorer (known inputs → known rankings; z-score edge cases: zero stddev, cold start).
- Collector tests against recorded fixture responses (no live API in tests).
- One end-to-end smoke test with fixtures producing a full HTML output.

## Out of Scope (this phase)
Auto-posting to platforms (use Publer/Buffer manually first), the AI character, the paid report storefront, X/TikTok/GitHub collectors (phase 2).

## Success Criteria
- Runs daily producing a Top-100 HTML + JSON in < 5 min.
- ≥3 sources contributing; dedup produces no obvious duplicate stories in top 20.
- Jaya can pick tomorrow's content topics from the YouTube brief in < 10 minutes.
