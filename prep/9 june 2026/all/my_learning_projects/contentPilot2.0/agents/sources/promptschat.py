import random
from datetime import datetime, UTC
import httpx
from core.trend_models import TrendItem, trend_id

API_URL = "https://datasets-server.huggingface.co/rows"
DATASET = "fka/prompts.chat"  # CC0 public domain, ~2k curated prompts
TOTAL_ROWS = 1984


class PromptsChatSource:
    """Proven prompt patterns from the CC0 prompts.chat dataset (HuggingFace).

    No engagement metric exists per prompt, so engagement stays 0 — these rank
    below live-viral Reddit/Civitai items but guarantee the demo is never empty.
    A random offset keeps refreshes varied.
    """

    def fetch(self, limit: int = 20) -> list[TrendItem]:
        offset = random.randint(0, max(TOTAL_ROWS - limit, 0))
        response = httpx.get(API_URL, params={
            "dataset": DATASET, "config": "default", "split": "train",
            "offset": offset, "length": min(limit, 100),
        }, timeout=20)
        response.raise_for_status()

        items: list[TrendItem] = []
        for entry in response.json().get("rows", []):
            row = entry.get("row", {})
            prompt = row.get("prompt", "")
            if not prompt:
                continue
            act = row.get("act", "")
            text = f"[{act}] {prompt}" if act else prompt
            items.append(TrendItem(
                id=trend_id("promptschat", prompt),
                prompt=text,
                source="promptschat",
                kind="text",
                source_url="https://prompts.chat",
                engagement=0,
                fetched_at=datetime.now(UTC),
            ))
        return items[:limit]
