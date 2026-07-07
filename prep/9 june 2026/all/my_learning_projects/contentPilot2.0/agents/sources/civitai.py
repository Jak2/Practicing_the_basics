import os
from datetime import datetime, UTC
import httpx
from core.trend_models import TrendItem, trend_id

API_URL = "https://civitai.com/api/v1/images"

# Reactions that count as engagement (dislikes excluded).
_REACTION_KEYS = ("likeCount", "heartCount", "laughCount", "cryCount")


class CivitaiSource:
    """Viral image prompts from Civitai's public REST API.

    Note: the API returns meta=None (no prompt) for unauthenticated requests.
    Set CIVITAI_API_TOKEN in .env to get live prompts; without it this source
    degrades to an empty list rather than failing the run.
    """

    def fetch(self, limit: int = 20) -> list[TrendItem]:
        params = {
            "limit": min(limit * 5, 200),  # over-fetch: many items lack meta.prompt
            "sort": "Most Reactions",
            "period": "Week",
            "nsfw": "None",
        }
        headers = {}
        token = os.getenv("CIVITAI_API_TOKEN", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = httpx.get(API_URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()

        items: list[TrendItem] = []
        for raw in response.json().get("items", []):
            prompt = (raw.get("meta") or {}).get("prompt")
            if not prompt:
                continue
            stats = raw.get("stats", {})
            engagement = sum(stats.get(k, 0) for k in _REACTION_KEYS)
            items.append(TrendItem(
                id=trend_id("civitai", prompt),
                prompt=prompt,
                source="civitai",
                kind="image",
                image_url=raw.get("url"),
                source_url=f"https://civitai.com/images/{raw.get('id')}",
                engagement=engagement,
                fetched_at=datetime.now(UTC),
            ))
            if len(items) >= limit:
                break
        return items
