# contentPilot2.0 — Viral Prompt Trend Engine (POC)

> **Date:** 2026-07-05
> **Status:** Approved via goal directive (user selected trend-intelligence approach,
> Gemini 2.0 Flash, dashboard push/delete control, image display in two AskUserQuestion
> rounds; build delegated via /goal).
> **Purpose:** Interview-ready POC demonstrating API integration, scoring algorithm
> design, LLM-powered analysis, and full-stack delivery on top of the Phase-4
> contentpilot architecture.

---

## 1. Problem Statement

contentPilot (1.0) discovers generic trending *topics* and writes posts about them.
contentPilot2.0 targets a sharper question: **which prompting designs are going viral
right now, and why?** It pulls actually-viral prompts (with their generated images)
from free, licensing-friendly sources, ranks them with an explainable virality score,
uses an LLM to extract *why each prompt works*, and presents everything in a dashboard
where the owner can turn any trend into a published post — or delete it — with one click.

## 2. Goals

- Fetch viral prompts from free sources (probed live 2026-07-05):
  - **Reddit** (praw, creds in .env) — primary viral source. Text prompts from
    r/ChatGPTPromptGenius + r/PromptEngineering; image prompts from r/StableDiffusion +
    r/midjourney (post image hotlinked, upvotes = engagement).
  - **Civitai** (public REST API) — adapter shipped + fixture-tested, but the API
    returns meta=None without an account token; live data requires free
    CIVITAI_API_TOKEN in .env, otherwise the source degrades to empty gracefully.
  - **prompts.chat via HuggingFace datasets-server** (CC0, 1984 rows) — always-on
    baseline of proven prompt patterns (engagement 0, ranked below live-viral items).
  - **Lexica dropped** — api/v1/search returns HTTP 500 (deprecated).
- Normalize into one `TrendItem` model; persist to `trends.json` (Pydantic + FileLock,
  same pattern as `manifest.json`).
- Score virality: log-scaled engagement normalized per source + recency boost. Pure
  function, unit-tested, explainable in one sentence.
- Extract insights per trend via Gemini 2.0 Flash: pattern tags, two-sentence
  "why viral", category. Graceful skip on API failure ("analysis pending").
- Dashboard `/trends` page: ranked cards with generated image (hotlinked), prompt,
  score bar, source badge, insight tags, and a **Draft post** button that feeds the
  trend into the existing ContentGenerator → drafts → approve/reject → push/delete flow.
- CLI: `python main.py trends --sources reddit,civitai,promptschat --top 20` (new Typer subcommand;
  existing `run` command unchanged).
- README "2-minute demo script" section for interview walkthroughs.

### Out of Scope (YAGNI)

- Embedding-based clustering / trend history over time
- Dashboard auth; multi-site adapters; paid sources (PromptBase, PromptHero Pro)
- Storing/downloading source images locally (hotlink only; CC0/API-permitted sources)

## 3. Architecture

```
agents/sources/__init__.py     source adapter registry
agents/sources/civitai.py      GET civitai.com/api/v1/images?sort=Most Reactions&period=Week
agents/sources/promptschat.py  GET datasets-server.huggingface.co/rows?dataset=fka/prompts.chat
agents/sources/reddit_trends.py praw: prompt subs (text) + SD/MJ subs (image posts)
core/trend_models.py           TrendItem, TrendState (Pydantic v2)
core/trend_store.py            load/save trends.json (FileLock, mirrors manifest.py)
core/virality.py               score(items) -> items with virality_score, sorted
agents/insight_extractor.py    Gemini JSON: {pattern_tags, why_viral, category}
agents/trend_engine.py         orchestrates: fetch -> score -> insight -> store (run_log traced)
main.py                        new `trends` subcommand (Typer)
dashboard/server.py            GET /trends, POST /api/trends/refresh, POST /api/trends/{id}/draft,
                               DELETE /api/trends/{id}
dashboard/templates/trends.html ranked trend cards
```

Each source adapter: `fetch(limit: int) -> list[TrendItem]` (partially filled; scorer
fills `virality_score`). One adapter failing must not kill the run (per-source
try/except, run_log step per source — existing TrendDiscovery pattern).

## 4. Data Model

```python
class TrendItem(BaseModel):
    id: str                      # sha1(source + prompt)[:12]
    prompt: str
    source: Literal["civitai", "promptschat", "reddit"]
    kind: Literal["image", "text"]
    image_url: str | None = None
    source_url: str = ""
    engagement: int = 0          # reactions / upvotes / points (raw, per source)
    virality_score: float = 0.0  # 0-100 normalized
    insight: TrendInsight | None = None
    fetched_at: datetime

class TrendInsight(BaseModel):
    pattern_tags: list[str]      # e.g. ["cinematic lighting", "artist token", "negative prompt"]
    why_viral: str               # 2 sentences
    category: str                # e.g. "portrait", "coding-assistant"

class TrendState(BaseModel):
    trends: list[TrendItem] = []
    last_refreshed: datetime | None = None
```

## 5. Virality Score

Per source, engagement ranges differ wildly (Civitai reactions ~10-5000, HN points
~50-2000). Score = `100 * log1p(engagement) / log1p(max_engagement_in_source_batch)`,
then a recency multiplier is out of scope for POC (sources already return current-week
hot items). Ties broken by raw engagement. Rationale: log tames whales, per-source
normalization makes cross-source ranking fair, and the whole thing is one testable
pure function.

## 6. Insight Extraction

One Gemini 2.0 Flash call per trend (batch of top N only — default 20 — to respect
free-tier quota). Prompt instructs strict JSON out; parse with Pydantic; on parse or
API failure store `insight=None` and continue. Ollama fallback documented but Gemini
default (phi3:mini hallucination risk noted in decisions_and_issues.md of 1.0).

## 7. Dashboard Flow

`/trends` renders `trends.json` ranked by score. Buttons per card:
- **Draft post** → POST `/api/trends/{id}/draft` → ContentGenerator writes an insight
  post about the trend → lands in existing `/drafts` queue → approve pushes to target
  repo, reject deletes. No bypass of the approval gate.
- **Delete** → DELETE `/api/trends/{id}` → removed from trends.json.
- **Refresh trends** button → POST `/api/trends/refresh` → runs trend_engine in
  executor (non-blocking, same pattern as /api/run-now).

## 8. Error Handling

- Source adapter exceptions caught per source; run continues with remaining sources.
- Gemini failures: trend kept, `insight=None`, card shows "analysis pending".
- trends.json missing → empty state page with "Refresh trends" CTA.
- All steps traced into run_log.json (existing new_step/finish_step helpers).

## 9. Testing

- Fixture JSON captured per source API shape; adapters tested against fixtures (mocked
  httpx/praw) — no live calls in suite.
- `core/virality.py`: known inputs → exact expected ranking + scores.
- Insight extractor: mocked Gemini; JSON-parse-failure path tested.
- Dashboard: /trends 200 with fixture state, draft button creates draft, delete removes.
- Existing 69 tests must stay green.

## 10. Demo Script (README)

1. `python main.py trends --top 10` (~30s)
2. Open dashboard /trends — ranked viral prompts with images + insights
3. Click Draft post on #1 → show /drafts → Approve → show git commit in target repo
4. Point at run_log /pipeline page — full execution trace
5. Punchline: every step (fetch, score, analyze, publish) automated but human-gated.
