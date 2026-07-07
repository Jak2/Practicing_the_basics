import sys
from datetime import datetime, UTC
from core.trend_models import TrendState
from core.trend_store import save_trends
from core.virality import score_trends
from core.run_log import new_run, new_step, finish_step, finish_run, append_run
from agents.sources import SOURCES
from agents.insight_extractor import InsightExtractor

DEFAULT_TRENDS = "trends.json"
DEFAULT_RUN_LOG = "run_log.json"


class TrendEngine:
    """fetch -> score -> analyze -> store. Every step traced into run_log.json."""

    def __init__(self, trends_path: str = DEFAULT_TRENDS, run_log_path: str = DEFAULT_RUN_LOG):
        self.trends_path = trends_path
        self.run_log_path = run_log_path

    def run(self, sources: list[str], top: int = 20, insight_top: int = 20) -> None:
        run = new_run()
        overall = "success"
        items = []

        # ── Fetch (per-source isolation) ─────────────────────────────────
        for name in sources:
            step = new_step(f"fetch_{name}", f"{name}.fetch()", f"agents/sources/{name}.py")
            try:
                fetched = SOURCES[name]().fetch(limit=top)
                items.extend(fetched)
                finish_step(step, "success", detail=f"{len(fetched)} trend(s)")
            except Exception as e:
                finish_step(step, "failed", error=str(e))
                overall = "partial"
                print(f"[ContentPilot2] source '{name}' failed: {e}", file=sys.stderr)
            run.steps.append(step)

        # ── Score ────────────────────────────────────────────────────────
        score_step = new_step("virality_score", "score_trends()", "core/virality.py")
        items = score_trends(items)[:top]
        finish_step(score_step, "success", detail=f"{len(items)} trend(s) ranked")
        run.steps.append(score_step)

        # ── Insights (top N only — respect LLM quota) ────────────────────
        if items:
            insight_step = new_step("insight_extract", "InsightExtractor.extract()", "agents/insight_extractor.py")
            extractor = InsightExtractor()
            analyzed = 0
            for item in items[:insight_top]:
                item.insight = extractor.extract(item)
                if item.insight:
                    analyzed += 1
            finish_step(insight_step, "success", detail=f"{analyzed}/{min(len(items), insight_top)} analyzed")
            run.steps.append(insight_step)

        # ── Store ────────────────────────────────────────────────────────
        save_trends(TrendState(trends=items, last_refreshed=datetime.now(UTC)), self.trends_path)
        finish_run(run, overall)
        append_run(run, self.run_log_path)
