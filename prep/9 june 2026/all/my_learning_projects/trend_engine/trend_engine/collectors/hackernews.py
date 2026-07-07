import logging

import requests

from . import base

logger = logging.getLogger(__name__)

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
MAX_STORIES = 60


@base.safe_collect
def collect(session=None):
    getter = session.get if session is not None else requests.get
    resp = getter(TOP_STORIES_URL, timeout=15)
    resp.raise_for_status()
    ids = resp.json()[:MAX_STORIES]

    items = []
    for story_id in ids:
        try:
            item_resp = getter(ITEM_URL.format(id=story_id), timeout=15)
            item_resp.raise_for_status()
            data = item_resp.json()
        except Exception:
            logger.warning("hackernews collector: failed to fetch item %s", story_id, exc_info=True)
            continue
        if not data or "title" not in data:
            continue
        title = data["title"]
        items.append({
            "topic_key": base.normalize_key(title),
            "source": "hackernews",
            "title": title,
            "url": data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "engagement": float(data.get("score", 0)),
            "engagement_type": "points",
            "region": "GLOBAL",
            "fetched_at": base.now_iso(),
            "content_created_at": base.epoch_to_iso(data.get("time")),
        })
    return items
