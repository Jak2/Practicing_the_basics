# Trend Engine

Daily pipeline that collects viral/trending signals (Hacker News, Reddit, YouTube,
Wikipedia), scores them, deduplicates + explains them with an LLM pass, and publishes a
ranked Top-100 report plus per-platform content briefs.

Design docs live in `my_learning_projects/0.roadmap_to_millionaire/` (`trend-engine-design.md`,
`trend-engine-plan.md`). This file is the day-to-day operator's manual.

## memory
/home/asterisk/.claude/projects/-media-asterisk-windows-drive-project-learn/memory/project_trend_engine_build.md

## Quick start

```bash
cd my_learning_projects/trend_engine
pip install -r requirements.txt   # first time only

cp .env.example .env              # then edit .env and paste in your keys (see below)
```

**Dashboard (recommended):**
```bash
python3 ui/server.py
```
Open **http://localhost:8765** — click **Launch Run**, watch the pipeline stages light
up (click any stage to expand what it's doing under the hood), and open the finished
report from the link that appears. The dashboard shows an environment checklist (are
your keys actually being picked up?), a live log, run history, and a foldable
step-by-step "How to use this" walkthrough — everything you need is on that one page.
No new dependencies — it's stdlib-only (`http.server`).

**Command line:**
```bash
python3 run_daily.py
```

Output lands in `output/<YYYY-MM-DD>/`:
- `top100.html` — the flagship ranked report (open this first)
- `top100.json` — same data, machine-readable
- `briefs/youtube.html`, `briefs/instagram.html`, `briefs/x.html` — per-platform content angles
- `run_log.md` (one level up, in `output/`) — one row appended per run: items/topics/enriched/duration

Run the test suite any time with `python3 -m pytest -v` (54 tests, no network/API keys needed).

## Getting the two API keys — `.env` setup

Keys live in a `.env` file at `trend_engine/.env`, loaded automatically (stdlib-only —
no `python-dotenv` dependency) every time `config.py` is imported, which every entry
point (`run_daily.py`, `ui/server.py`, tests) does. **You never need to `export`
anything in your shell.** A shell-exported var, if you do set one, always wins over
`.env` (normal dotenv precedence) — useful for a one-off override.

```bash
cp .env.example .env
```
Then edit `.env`:
```bash
YOUTUBE_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

**YouTube Data API v3 key** (free, 10,000 units/day — this pipeline uses ~200/run):
1. https://console.cloud.google.com/ → new project → **APIs & Services → Library** → enable "YouTube Data API v3"
2. **APIs & Services → Credentials** → **Create Credentials → API key**
3. (Recommended) restrict the key to YouTube Data API v3 only
4. Paste it into `.env` as `YOUTUBE_API_KEY=...`

**Anthropic API key** (pay-as-you-go, ~$0.05–0.08/day at this pipeline's volume):
1. https://console.anthropic.com/ → **API Keys → Create Key**
2. Add a small credit balance (Billing)
3. Paste it into `.env` as `ANTHROPIC_API_KEY=...`

Never commit `.env`. `.gitignore` excludes `.env` and `.env.*` (but explicitly allows
`.env.example`, which is the template and IS meant to be committed — it has no real keys).

## Configuring what it searches — `trend_engine/config.py`

Everything about *scope* is edit-and-rerun, no code changes needed elsewhere.

| Setting | Controls |
|---|---|
| `SUBREDDITS` | Which subreddits Reddit collector pulls from |
| `YOUTUBE_REGIONS` | Which YouTube trending regions (e.g. `["US","IN"]`) |
| `YOUTUBE_CATEGORY_IDS` | Which YouTube category IDs to keep (default `["28","24"]` = Science&Tech, Entertainment; empty list = no filter) |
| `NICHE_AI_KEYWORDS` / `NICHE_INDIA_KEYWORDS` | Boost (not filter) scores for matching topics (×1.5 / ×1.3, stackable) |
| `EXCLUDE_KEYWORDS` | **Hard filter** — topics matching these are dropped entirely before scoring (sports, obituaries, celebrity noise by default) |
| `SOURCE_ENABLED` | Turn any collector fully on/off by name: `hackernews`, `reddit`, `youtube`, `wikipedia` |
| `ANTHROPIC_MODEL` | Swap the enrichment model |

**Adding a new niche category** (e.g. finance): a commented-out example already sits in
both `config.py` (`NICHE_FINANCE_KEYWORDS`) and `score.py`'s `niche_weight()` — uncomment
both blocks and adjust the keyword list and weight.

**Example — retarget toward finance/crypto:**
```python
SUBREDDITS = ["CryptoCurrency", "wallstreetbets", "finance", "IndianStockMarket"]
EXCLUDE_KEYWORDS = ["cricket", "football", "nba"]  # keep or drop as you like
```

## Reading the output

- **Score** — a composite of spike-detection (z-score vs the topic's own 7-day history,
  or a same-day percentile for brand-new topics), recency decay, cross-source
  corroboration, and niche weighting. Higher = more worth covering right now. Recency
  decay uses the content's actual creation time when the source provides one (Hacker
  News `time`, Reddit `<updated>`, YouTube `publishedAt`) — Wikipedia has no such
  timestamp (it's a daily aggregate), so it falls back to collection time.
- **Stage badge** — `early-signal` / `rising` / `peaking` (LLM-assigned; absent in
  degraded runs).
- **Degraded run** (red banner on `top100.html`) — means the Anthropic API call failed
  (or no key was set); you still get math-only rankings but no dedup/explanations, and
  the platform briefs will be empty (they're built from LLM-assigned `platform_fit` tags).

## Running it automatically (cron)

`run_daily.py` writes into paths relative to the repo, so cron needs an absolute working
directory. Keys come from `.env` (the same file from the Quick Start section above) —
since `config.py` loads it automatically, cron does **not** need its own copy of your
shell's exported variables; just make sure `.env` exists in `trend_engine/`.

1. `trend_engine/run_cron.sh` already exists in this repo — verify it's executable:
   ```bash
   chmod +x my_learning_projects/trend_engine/run_cron.sh
   ```
2. Add the cron entry (`crontab -e`) — runs daily at 06:00 local time:
   ```cron
   0 6 * * * /media/asterisk/windows_drive/project/learn/my_learning_projects/trend_engine/run_cron.sh
   ```
3. Verify it's registered: `crontab -l`
4. Check `output/cron.log` and `output/run_log.md` the next morning to confirm it ran.

To change the time, edit the first five fields (`minute hour day month weekday`) —
e.g. `30 8 * * *` runs at 08:30 daily. To stop the schedule, `crontab -e` and delete the line.

## Troubleshooting

- **Reddit collector logs 429 errors** — Reddit rate-limits rapid unauthenticated
  requests. The collector already paces fetches (`reddit.PACE_SECONDS`, default 10s
  between subreddits); if it still 429s during a run, that's expected occasionally and
  the collector skips that subreddit and continues (never crashes the run).
  Missing subreddits just mean fewer topics that day, not a failure.
- **Wikipedia returns 0 items** — Wikimedia requires a descriptive User-Agent; this is
  already set in `collectors/base.py`. If it still fails, check the live endpoint
  manually: `curl -A "trend-engine/0.1" https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/YYYY/MM/DD`.
- **Every run is "degraded"** — check `.env` has `ANTHROPIC_API_KEY` set and the account
  has credit; check `output/cron.log` (if run via cron) or the dashboard's live log for
  the actual exception.
- **`python` not found** — this project uses `python3` explicitly everywhere.
- **Dashboard says "already running" (409) but nothing seems to be happening** — a
  previous run may not have exited cleanly; check `output/ui_run.log` and, if needed,
  stop the dashboard server (Ctrl+C) and restart it.
- **Checklist shows a key as "not set" even though `.env` has it** — check for typos in
  the key name (`YOUTUBE_API_KEY` / `ANTHROPIC_API_KEY`, no quotes needed around the
  value, no spaces around `=`), and that `.env` is directly inside `trend_engine/` (not
  a subfolder). Restart `ui/server.py` after editing `.env` — it's only read at import
  time, not re-read live.

## Problems you're likely to run into (and what they mean)

Being upfront about the rough edges you'll probably hit while using this day to day:

1. **First run after setup often looks "worse" than expected.** With no history yet,
   every topic is brand-new, so ranking falls back to same-day percentile rather than
   the (better) 7-day spike detection. This corrects itself after a few days of runs
   build up history in `trends.db` — it's not a bug, just a cold-start reality.
2. **Reddit subreddits will intermittently 429 and get skipped**, especially if you
   launch multiple runs close together (e.g. testing). This is Reddit's public rate
   limit, not something in our control beyond the current pacing. Expect some days to
   have fewer Reddit-sourced topics than others.
3. **A "successful" run can still be degraded** — exit code 0 and a green badge just
   mean the pipeline didn't crash; check the run history's "Enriched" column (or the red
   banner on the report) to know if you actually got explanations or just raw rankings.
   Easy to mistake "it ran" for "it worked as intended."
4. **Wikipedia and YouTube pull in off-niche noise.** Wikipedia's global top-pageviews
   list includes celebrities/sports/obituaries; `EXCLUDE_KEYWORDS` catches some but not
   all of it. YouTube's trending feed isn't category-filtered, so music/general
   entertainment videos can outrank genuinely relevant tech/AI content. Expect to keep
   tuning `EXCLUDE_KEYWORDS` and `NICHE_*_KEYWORDS` as you notice junk in the Top-100.
5. **Anthropic costs real money per run** (~$0.05–0.08/day at current settings) — cheap,
   but not zero. If you launch runs repeatedly while testing/tuning config, that adds up
   faster than one-run-a-day would. The dashboard has no cost guardrail; that's on you
   to self-monitor for now.
6. **Cost/behavior scale with how many keywords and subreddits you add** — more
   subreddits means more Reddit fetches (more 429 risk with the same pacing); a huge
   `EXCLUDE_KEYWORDS`/niche list has negligible cost (it's local regex) but a bloated
   `SUBREDDITS` list will make runs noticeably slower.
7. **Editing `.env` while the dashboard server is running has no effect** until you
   restart `ui/server.py` — env vars are loaded once at process start via Python's
   `os.environ.setdefault`, not re-read per request.
8. **The dashboard's "what's happening" live note is best-effort text-pattern matching**
   on the log, not a real structured signal from the pipeline — it can occasionally lag
   or mislabel which stage is active (e.g. right at the collect→score handoff, since
   scoring doesn't print anything). The stage colors (amber/green/red) and the actual
   log content underneath are the ground truth if the label looks wrong.
9. **If you kill the dashboard server mid-run** (Ctrl+C), the spawned `run_daily.py`
   subprocess may keep running in the background even after the dashboard is gone —
   check `pgrep -af run_daily.py` and kill it manually if so, since the dashboard's
   process tracking only exists while the server itself is alive.

## Project layout

```
trend_engine/
├── .env.example           # template — copy to .env and fill in your keys
├── config.py           # all tunable scope/behavior settings; loads .env on import
├── env_loader.py         # stdlib .env parser (no python-dotenv dependency)
├── store.py             # SQLite schema + queries (trends.db, gitignored)
├── score.py              # z-score/decay/corroboration/niche scoring, hard excludes
├── enrich.py              # single Anthropic Haiku call: dedup + explain + tag
├── publish.py              # HTML/JSON report + platform briefs
├── collectors/
│   ├── hackernews.py, reddit.py, youtube.py, wikipedia.py
│   └── base.py             # shared UA, normalize_key, safe_collect decorator
├── run_daily.py            # orchestrator — the entry point
├── run_cron.sh              # cron wrapper (see "Running it automatically")
├── ui/
│   ├── server.py             # stdlib http.server dashboard backend (port 8765)
│   └── index.html             # dashboard: foldable pipeline stages, launch, log, history, how-to
└── tests/                    # 54 tests, fixture-based, no live network calls
```
