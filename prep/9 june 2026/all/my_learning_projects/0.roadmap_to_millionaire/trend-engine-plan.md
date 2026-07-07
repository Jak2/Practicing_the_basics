# Trend Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the daily LLM-augmented pipeline that produces a ranked, enriched Top-100 viral-trends report (HTML + JSON + per-platform briefs).

**Architecture:** Linear pipeline — collectors (Reddit/HN/YouTube/Wikipedia) → SQLite store with 7-day history → deterministic scorer (z-score × decay × corroboration × niche weight) → single Haiku enrichment call (dedup/explain/tag, with degraded mode) → HTML/JSON publisher. See `trend-engine-design.md`.

**Tech Stack:** Python 3.10+, stdlib `sqlite3`, `requests`, `pytest`, `anthropic` SDK (enricher only). No frameworks.

## Global Constraints

- All code lives in `my_learning_projects/trend_engine/` (repo root for this project; `git init` in Task 1).
- Collectors NEVER raise out of `collect()` — on any error they log and return `[]`.
- Scorer is pure math: no network, no LLM, fully deterministic given DB state.
- Enricher uses model `claude-haiku-4-5-20251001`; on failure after 1 retry, pipeline publishes math-only rankings (degraded mode) — never zero output.
- Tests never hit live APIs — fixtures only (JSON files in `tests/fixtures/`).
- DB `raw_items` is append-only.
- Niche keyword weights: AI/tech ×1.5, India ×1.3 (stackable, from design doc).
- Decay: `1 / (age_hours + 2)**1.8`. Corroboration multiplier: 1 source=1.0, 2=1.5, 3+=2.0.

---

### Task 1: Scaffold, config, and store

**Files:**
- Create: `trend_engine/{__init__.py,config.py,store.py}`, `requirements.txt`, `.gitignore`, `pytest.ini`
- Test: `tests/test_store.py`

**Interfaces:**
- Produces: `store.connect(db_path) -> sqlite3.Connection` (creates schema),
  `store.insert_items(conn, items: list[dict])`, `store.topic_history(conn, topic_key: str, days: int = 7) -> list[float]` (daily engagement sums, oldest first, excluding today),
  `store.todays_topics(conn) -> list[dict]` (per topic_key: `{"topic_key", "title", "engagement", "sources": [..], "regions": [..], "first_seen_hours": float, "urls": [..]}`),
  `config.SUBREDDITS`, `config.NICHE_AI_KEYWORDS`, `config.NICHE_INDIA_KEYWORDS`, `config.DB_PATH`.
- Item dict shape (used by ALL collectors): `{"topic_key": str, "source": str, "title": str, "url": str, "engagement": float, "engagement_type": str, "region": str, "fetched_at": iso8601 str}`.

- [ ] **Step 1: Scaffold**

```bash
cd /media/asterisk/windows_drive/project/learn/my_learning_projects
mkdir -p trend_engine/trend_engine trend_engine/tests/fixtures trend_engine/output
cd trend_engine && git init
printf 'requests\npytest\nanthropic\n' > requirements.txt
printf '__pycache__/\n*.db\noutput/\n.env\n' > .gitignore
printf '[pytest]\ntestpaths = tests\n' > pytest.ini
touch trend_engine/__init__.py
pip install -r requirements.txt
```

- [ ] **Step 2: Write config**

```python
# trend_engine/config.py
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "trends.db"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

SUBREDDITS = ["artificial", "OpenAI", "LocalLLaMA", "technology", "singularity", "india", "developersIndia"]
YOUTUBE_REGIONS = ["US", "IN"]

NICHE_AI_KEYWORDS = ["ai", "gpt", "llm", "openai", "anthropic", "claude", "gemini", "model", "agent", "robot", "neural", "chatbot", "deepmind", "nvidia"]
NICHE_INDIA_KEYWORDS = ["india", "indian", "delhi", "mumbai", "bengaluru", "bollywood", "rupee", "modi", "ipl", "desi"]

ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
```

- [ ] **Step 3: Write failing store tests**

```python
# tests/test_store.py
import datetime as dt
from trend_engine import store

def _item(topic="gpt-6 leak", eng=100.0, source="hackernews", region="GLOBAL", fetched_at=None):
    return {"topic_key": topic, "source": source, "title": topic.title(), "url": "https://x.com/1",
            "engagement": eng, "engagement_type": "points", "region": region,
            "fetched_at": (fetched_at or dt.datetime.now(dt.timezone.utc)).isoformat()}

def test_schema_created(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"raw_items", "daily_top100"} <= names

def test_insert_and_todays_topics(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(eng=50), _item(eng=70, source="reddit")])
    topics = store.todays_topics(conn)
    assert len(topics) == 1
    t = topics[0]
    assert t["topic_key"] == "gpt-6 leak"
    assert t["engagement"] == 120
    assert sorted(t["sources"]) == ["hackernews", "reddit"]

def test_topic_history_excludes_today(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    now = dt.datetime.now(dt.timezone.utc)
    for d, eng in [(3, 10), (2, 20), (1, 30), (0, 999)]:
        store.insert_items(conn, [_item(eng=eng, fetched_at=now - dt.timedelta(days=d))])
    assert store.topic_history(conn, "gpt-6 leak", days=7) == [10.0, 20.0, 30.0]
```

- [ ] **Step 4: Run tests, verify FAIL** — `pytest tests/test_store.py -v` → import error / AttributeError.

- [ ] **Step 5: Implement store**

```python
# trend_engine/store.py
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_items (
  id INTEGER PRIMARY KEY, topic_key TEXT NOT NULL, source TEXT NOT NULL,
  title TEXT, url TEXT, engagement REAL, engagement_type TEXT,
  region TEXT, fetched_at TEXT NOT NULL,
  fetched_date TEXT GENERATED ALWAYS AS (substr(fetched_at, 1, 10)) STORED
);
CREATE INDEX IF NOT EXISTS idx_raw_topic_date ON raw_items(topic_key, fetched_date);
CREATE TABLE IF NOT EXISTS daily_top100 (
  run_date TEXT, rank INTEGER, topic_key TEXT, title TEXT, score REAL,
  explanation TEXT, category TEXT, platform_fit TEXT, stage TEXT, urls TEXT,
  PRIMARY KEY (run_date, rank)
);
"""

def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    return conn

def insert_items(conn, items):
    conn.executemany(
        "INSERT INTO raw_items (topic_key, source, title, url, engagement, engagement_type, region, fetched_at)"
        " VALUES (:topic_key, :source, :title, :url, :engagement, :engagement_type, :region, :fetched_at)",
        items)
    conn.commit()

def topic_history(conn, topic_key, days=7):
    rows = conn.execute(
        "SELECT fetched_date, SUM(engagement) FROM raw_items"
        " WHERE topic_key = ? AND fetched_date < date('now')"
        "   AND fetched_date >= date('now', ?)"
        " GROUP BY fetched_date ORDER BY fetched_date",
        (topic_key, f"-{days} days")).fetchall()
    return [float(r[1]) for r in rows]

def todays_topics(conn):
    rows = conn.execute(
        "SELECT topic_key, MAX(title), SUM(engagement),"
        "       GROUP_CONCAT(DISTINCT source), GROUP_CONCAT(DISTINCT region),"
        "       (julianday('now') - julianday(MIN(fetched_at))) * 24,"
        "       GROUP_CONCAT(DISTINCT url)"
        " FROM raw_items WHERE fetched_date = date('now') GROUP BY topic_key").fetchall()
    return [{"topic_key": r[0], "title": r[1], "engagement": float(r[2]),
             "sources": r[3].split(","), "regions": r[4].split(","),
             "first_seen_hours": float(r[5]), "urls": r[6].split(",")} for r in rows]
```

- [ ] **Step 6: Run tests, verify PASS** — `pytest tests/test_store.py -v`
- [ ] **Step 7: Commit** — `git add -A && git commit -m "feat: scaffold, config, sqlite store"`

---

### Task 2: Scorer

**Files:**
- Create: `trend_engine/score.py` · Test: `tests/test_score.py`

**Interfaces:**
- Consumes: `store.todays_topics`, `store.topic_history` (Task 1).
- Produces: `score.zscore(today: float, history: list[float]) -> float`,
  `score.decay(age_hours: float) -> float`,
  `score.corroboration(n_sources: int) -> float`,
  `score.niche_weight(title: str) -> float`,
  `score.rank_topics(conn, limit: int = 150) -> list[dict]` — topics dicts from `todays_topics` each gaining `"score": float`, sorted desc, truncated to `limit`.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_score.py
import datetime as dt
from trend_engine import score, store
from tests.test_store import _item

def test_zscore_spike():
    assert score.zscore(8400, [210, 180, 240, 195, 220, 205]) > 100

def test_zscore_zero_stddev_and_cold_start():
    assert score.zscore(100, [50, 50, 50]) > 0          # eps guard, no ZeroDivisionError
    assert score.zscore(100, []) == 1.0                 # cold start: neutral 1.0

def test_decay_monotonic():
    assert score.decay(1) > score.decay(10) > score.decay(100)

def test_corroboration():
    assert [score.corroboration(n) for n in (1, 2, 3, 5)] == [1.0, 1.5, 2.0, 2.0]

def test_niche_weight_stacks():
    assert score.niche_weight("Random cooking video") == 1.0
    assert score.niche_weight("New AI model") == 1.5
    assert abs(score.niche_weight("AI boom in India") - 1.95) < 1e-9

def test_rank_topics_orders_and_limits(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(topic="ai spike", eng=5000),
                              _item(topic="flat story", eng=100)])
    ranked = score.rank_topics(conn, limit=1)
    assert len(ranked) == 1 and ranked[0]["topic_key"] == "ai spike"
    assert ranked[0]["score"] > 0
```

- [ ] **Step 2: Run, verify FAIL** — `pytest tests/test_score.py -v`
- [ ] **Step 3: Implement**

```python
# trend_engine/score.py
import statistics
from . import config, store

EPS = 1e-6

def zscore(today, history):
    if not history:
        return 1.0
    mean = statistics.mean(history)
    std = statistics.pstdev(history)
    return (today - mean) / max(std, EPS) if len(history) > 1 else (today - mean) / max(abs(mean), EPS)

def decay(age_hours):
    return 1.0 / (age_hours + 2) ** 1.8

def corroboration(n_sources):
    return 1.0 if n_sources <= 1 else (1.5 if n_sources == 2 else 2.0)

def niche_weight(title):
    words = title.lower()
    w = 1.0
    if any(k in words for k in config.NICHE_AI_KEYWORDS):
        w *= 1.5
    if any(k in words for k in config.NICHE_INDIA_KEYWORDS):
        w *= 1.3
    return w

def rank_topics(conn, limit=150):
    topics = store.todays_topics(conn)
    if not topics:
        return []
    zs = {t["topic_key"]: zscore(t["engagement"], store.topic_history(conn, t["topic_key"])) for t in topics}
    zmax = max(max(zs.values()), EPS)
    for t in topics:
        z_norm = max(zs[t["topic_key"]], 0) / zmax
        d = decay(t["first_seen_hours"])
        t["score"] = z_norm * (0.5 + 0.5 * d) * corroboration(len(t["sources"])) * niche_weight(t["title"])
    return sorted(topics, key=lambda t: t["score"], reverse=True)[:limit]
```

- [ ] **Step 4: Run, verify PASS** — `pytest tests/test_score.py -v`
- [ ] **Step 5: Commit** — `git commit -am "feat: deterministic scorer (zscore, decay, corroboration, niche)"`

---

### Task 3: Collectors (HN, Reddit, YouTube, Wikipedia)

**Files:**
- Create: `trend_engine/collectors/{__init__.py,base.py,hackernews.py,reddit.py,youtube.py,wikipedia.py}`
- Create fixtures: `tests/fixtures/{hn_top.json,hn_item.json,reddit_hot.json,yt_trending.json,wiki_views.json}`
- Test: `tests/test_collectors.py`

**Interfaces:**
- Consumes: item dict shape from Task 1.
- Produces: each module exposes `collect(session=None) -> list[dict]` (item dicts; empty list on any error). `base.normalize_key(title: str) -> str` (lowercase, strip punctuation, collapse whitespace). `collectors.ALL = [hackernews, reddit, youtube, wikipedia]`.
- YouTube requires env var `YOUTUBE_API_KEY`; returns `[]` with a log line if unset.

- [ ] **Step 1: Write fixtures** — realistic minimal JSON copied from each API's documented response shape. Examples:

```json
// tests/fixtures/hn_top.json
[101, 102]
```
```json
// tests/fixtures/hn_item.json
{"id": 101, "title": "GPT-6 leaked benchmarks", "score": 934, "descendants": 512,
 "time": 1751400000, "url": "https://example.com/gpt6"}
```
```json
// tests/fixtures/reddit_hot.json
{"data": {"children": [{"data": {"title": "GPT-6 leaked benchmarks!!", "ups": 4200,
 "num_comments": 800, "permalink": "/r/artificial/x", "created_utc": 1751400000}}]}}
```
```json
// tests/fixtures/yt_trending.json
{"items": [{"id": "abc", "snippet": {"title": "GPT-6 is INSANE"},
 "statistics": {"viewCount": "1200000", "likeCount": "90000"}}]}
```
```json
// tests/fixtures/wiki_views.json
{"items": [{"articles": [{"article": "GPT-6", "views": 250000, "rank": 12}]}]}
```

- [ ] **Step 2: Write failing tests** (mock `requests` with fixture payloads; test normalization, error swallowing)

```python
# tests/test_collectors.py
import json, pathlib
from unittest.mock import patch, MagicMock
from trend_engine.collectors import base, hackernews, reddit

FIX = pathlib.Path(__file__).parent / "fixtures"

def _resp(payload):
    m = MagicMock(); m.json.return_value = payload; m.raise_for_status.return_value = None
    return m

def test_normalize_key():
    assert base.normalize_key("GPT-6  Leaked, Benchmarks!!") == "gpt 6 leaked benchmarks"

def test_hn_collect_maps_fields():
    ids = json.loads((FIX / "hn_top.json").read_text())
    item = json.loads((FIX / "hn_item.json").read_text())
    with patch("trend_engine.collectors.hackernews.requests.get",
               side_effect=[_resp(ids)] + [_resp(item)] * len(ids)):
        out = hackernews.collect()
    assert out and out[0]["source"] == "hackernews" and out[0]["engagement"] == 934
    assert out[0]["topic_key"] == "gpt 6 leaked benchmarks"

def test_reddit_collect_and_error_swallow():
    payload = json.loads((FIX / "reddit_hot.json").read_text())
    with patch("trend_engine.collectors.reddit.requests.get", return_value=_resp(payload)):
        out = reddit.collect()
    assert out and out[0]["source"] == "reddit" and out[0]["engagement"] == 4200
    with patch("trend_engine.collectors.reddit.requests.get", side_effect=Exception("down")):
        assert reddit.collect() == []
```

- [ ] **Step 3: Run, verify FAIL**
- [ ] **Step 4: Implement `base.py`** (shared: `normalize_key`, `now_iso`, `safe_collect` decorator that try/excepts, logs, returns `[]`) — then each collector:
  - `hackernews.py`: GET `https://hacker-news.firebaseio.com/v0/topstories.json` (first 60 ids), then each item; engagement = points; region GLOBAL.
  - `reddit.py`: per configured subreddit GET `https://www.reddit.com/r/<sub>/hot.json?limit=25` with a custom User-Agent; engagement = ups; region IN for India subs else GLOBAL.
  - `youtube.py`: GET `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode=<US|IN>&maxResults=50&key=$YOUTUBE_API_KEY`; engagement = viewCount/1000 (normalize scale); region per request.
  - `wikipedia.py`: GET top pageviews `https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{Y}/{M}/{D}` (yesterday); engagement = views/1000; skip boilerplate pages (Main_Page, Special:*).
  - All apply `base.normalize_key(title)` → `topic_key`; all wrapped by `safe_collect`.
  - `__init__.py`: `from . import hackernews, reddit, youtube, wikipedia; ALL = [hackernews, reddit, youtube, wikipedia]`
- [ ] **Step 5: Run, verify PASS** — `pytest tests/test_collectors.py -v`
- [ ] **Step 6: Manual live smoke (one time):** `python -c "from trend_engine.collectors import hackernews; print(len(hackernews.collect()))"` → expect > 0.
- [ ] **Step 7: Commit** — `git commit -am "feat: HN/Reddit/YouTube/Wikipedia collectors with safe error handling"`

---

### Task 4: Enricher

**Files:**
- Create: `trend_engine/enrich.py` · Test: `tests/test_enrich.py`

**Interfaces:**
- Consumes: ranked topic dicts from `score.rank_topics` (have `topic_key,title,score,sources,urls`).
- Produces: `enrich.enrich(candidates: list[dict]) -> tuple[list[dict], bool]` — (final topics ≤100, enriched_flag). Each output dict adds `"explanation": str, "category": str, "platform_fit": str, "stage": str`; merged clusters sum scores and keep highest-scored title. On LLM failure (after 1 retry): returns first 100 candidates with `explanation=""`, `category="unclassified"`, `platform_fit=""`, `stage=""` and `enriched_flag=False`.
- Internal: `enrich._call_llm(payload: str) -> str` (isolated for mocking), `enrich._parse(response_text, candidates) -> list[dict]` (validates JSON, raises `ValueError` on bad shape).

- [ ] **Step 1: Write failing tests**

```python
# tests/test_enrich.py
import json
from unittest.mock import patch
from trend_engine import enrich

CANDS = [{"topic_key": "gpt 6 leaked benchmarks", "title": "GPT-6 leaked benchmarks", "score": 9.1,
          "sources": ["hackernews", "reddit"], "urls": ["u1"]},
         {"topic_key": "gpt 6 is insane", "title": "GPT-6 is INSANE", "score": 4.0,
          "sources": ["youtube"], "urls": ["u2"]}]

GOOD = json.dumps({"topics": [{"canonical_key": "gpt 6 leaked benchmarks",
        "merged_keys": ["gpt 6 is insane"], "explanation": "Leaked GPT-6 benchmarks are spreading.",
        "category": "AI", "platform_fit": "short-video", "stage": "rising"}]})

def test_enrich_merges_and_annotates():
    with patch.object(enrich, "_call_llm", return_value=GOOD):
        out, ok = enrich.enrich(CANDS)
    assert ok and len(out) == 1
    assert out[0]["score"] == 13.1 and out[0]["category"] == "AI"

def test_degraded_mode_after_retry():
    with patch.object(enrich, "_call_llm", side_effect=Exception("api down")) as m:
        out, ok = enrich.enrich(CANDS)
    assert not ok and len(out) == 2 and out[0]["category"] == "unclassified"
    assert m.call_count == 2  # one retry

def test_parse_rejects_bad_json():
    import pytest
    with pytest.raises(ValueError):
        enrich._parse("not json at all", CANDS)
```

- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement** — `_call_llm` uses `anthropic.Anthropic().messages.create(model=config.ANTHROPIC_MODEL, max_tokens=8000, messages=[...])` with a prompt instructing: cluster same-story topics, one-line "why viral" explanation in a sharp analyst voice, category ∈ {AI, tech, India, meme, other}, platform_fit ∈ {short-video, thread, long-form}, stage ∈ {early-signal, rising, peaking}; **return JSON only** matching the schema in the test. `_parse` json-loads (stripping code fences), validates required keys, maps clusters back onto candidate dicts (sum scores of merged members, drop merged members), passes through unmentioned candidates unchanged, truncates to 100. `enrich()` orchestrates: try `_parse(_call_llm(...))`, retry once, else degraded mode.
- [ ] **Step 4: Run, verify PASS** — `pytest tests/test_enrich.py -v`
- [ ] **Step 5: Commit** — `git commit -am "feat: LLM enricher with dedup, tagging, degraded mode"`

---

### Task 5: Publisher

**Files:**
- Create: `trend_engine/publish.py` · Test: `tests/test_publish.py`

**Interfaces:**
- Consumes: enriched topic dicts from Task 4 (+ `enriched_flag`).
- Produces: `publish.publish(topics: list[dict], enriched: bool, run_date: str, out_root: Path) -> Path` — writes `out_root/<run_date>/top100.html`, `top100.json`, `briefs/{youtube,instagram,x}.html`; returns the day directory. Also `publish.save_to_db(conn, topics, run_date)` inserting into `daily_top100`.
- Brief filters: youtube ← `platform_fit == "short-video" or "long-form"`, x ← `"thread"`, instagram ← `"short-video"`.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_publish.py
import json
from trend_engine import publish, store

TOPICS = [{"topic_key": "gpt 6", "title": "GPT-6 leak", "score": 13.1, "urls": ["u1"],
           "sources": ["hackernews"], "explanation": "Benchmarks leaked.", "category": "AI",
           "platform_fit": "short-video", "stage": "rising"}]

def test_publish_writes_files(tmp_path):
    day = publish.publish(TOPICS, enriched=True, run_date="2026-07-02", out_root=tmp_path)
    assert (day / "top100.html").exists() and (day / "briefs" / "youtube.html").exists()
    data = json.loads((day / "top100.json").read_text())
    assert data["topics"][0]["title"] == "GPT-6 leak" and data["enriched"] is True

def test_degraded_banner(tmp_path):
    day = publish.publish(TOPICS, enriched=False, run_date="2026-07-02", out_root=tmp_path)
    assert "degraded" in (day / "top100.html").read_text().lower()

def test_save_to_db(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    publish.save_to_db(conn, TOPICS, "2026-07-02")
    assert conn.execute("SELECT COUNT(*) FROM daily_top100").fetchone()[0] == 1
```

- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement** — HTML via a module-level template string in the same dark theme as the existing platform briefs (`#0f1117` bg, `#7dd3fc` headings); each topic row shows rank, title (linked to first url), score, stage badge, category, explanation. Degraded runs show a red banner: "⚠ Degraded run — math-only rankings, no LLM enrichment." JSON: `{"run_date", "enriched", "topics": [...]}` verbatim dicts. Briefs iterate filtered topics with a per-platform format hint line (YouTube: "Shorts angle: hook with the explanation line"; X: "Thread starter: post the explanation as the hook tweet").
- [ ] **Step 4: Run, verify PASS** — `pytest tests/test_publish.py -v`
- [ ] **Step 5: Commit** — `git commit -am "feat: HTML/JSON publisher with platform briefs and degraded banner"`

---

### Task 6: Orchestrator + end-to-end smoke

**Files:**
- Create: `run_daily.py` (project root) · Test: `tests/test_e2e.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `python run_daily.py` runs collect → store → score → enrich → publish, appends one summary line to `output/run_log.md` (`| date | items | topics | enriched | duration_s |`), exits 0 even when some collectors fail; exits 1 only if zero items were collected from all sources.

- [ ] **Step 1: Write failing e2e test** (all collectors mocked with fixture items; `_call_llm` mocked)

```python
# tests/test_e2e.py
import json, pathlib
from unittest.mock import patch
import run_daily
from tests.test_store import _item

def test_full_pipeline(tmp_path):
    fake_items = [_item(topic="ai everywhere", eng=999), _item(topic="ai everywhere", eng=500, source="reddit")]
    llm = json.dumps({"topics": [{"canonical_key": "ai everywhere", "merged_keys": [],
        "explanation": "AI is everywhere today.", "category": "AI",
        "platform_fit": "short-video", "stage": "peaking"}]})
    with patch("run_daily.collect_all", return_value=fake_items), \
         patch("trend_engine.enrich._call_llm", return_value=llm):
        code = run_daily.main(db_path=tmp_path / "t.db", out_root=tmp_path / "out")
    assert code == 0
    days = list((tmp_path / "out").iterdir())
    assert any((d / "top100.html").exists() for d in days if d.is_dir())

def test_exit_1_when_nothing_collected(tmp_path):
    with patch("run_daily.collect_all", return_value=[]):
        assert run_daily.main(db_path=tmp_path / "t.db", out_root=tmp_path / "out") == 1
```

- [ ] **Step 2: Run, verify FAIL**
- [ ] **Step 3: Implement `run_daily.py`** — `collect_all()` concatenates `m.collect()` for `collectors.ALL`; `main(db_path=config.DB_PATH, out_root=config.OUTPUT_DIR)` wires the stages, times the run, writes `run_log.md` line, returns exit code; `if __name__ == "__main__": sys.exit(main())`.
- [ ] **Step 4: Run FULL suite, verify PASS** — `pytest -v` (all tasks' tests).
- [ ] **Step 5: First real run** — `ANTHROPIC_API_KEY=... python run_daily.py` → open `output/<today>/top100.html`, verify a plausible Top-N renders (day 1 has no history, so all cold-start scores — expected).
- [ ] **Step 6: Commit** — `git commit -am "feat: daily orchestrator + e2e smoke"`

---

## Self-Review Notes

- Spec coverage: collectors ✓ (4 MVP sources), store/history ✓, scorer formula ✓ (matches design constants), enricher dedup/explain/tag + degraded mode ✓, publisher HTML/JSON/briefs ✓, run log ✓, <5min/<$0.05 targets respected (60 HN ids, 1 Haiku batch). Phase-2 items (TikTok CC, GitHub, Google Trends, mem0, Supabase) intentionally absent per design.
- Types consistent: item dict defined once (Task 1) and consumed by Tasks 2–6; `enrich.enrich` returns `(list, bool)` and publisher consumes exactly that.
- No placeholders: every step names exact endpoints, formulas, schemas, or complete code.
