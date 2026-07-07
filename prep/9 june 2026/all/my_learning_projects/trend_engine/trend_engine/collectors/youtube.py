import logging
import os

import requests

from . import base
from .. import config

logger = logging.getLogger(__name__)

VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


@base.safe_collect
def collect(session=None):
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        logger.info("YOUTUBE_API_KEY not set; skipping youtube collector")
        return []

    getter = session.get if session is not None else requests.get

    items = []
    for region in config.YOUTUBE_REGIONS:
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": 50,
            "key": api_key,
        }
        try:
            resp = getter(VIDEOS_URL, params=params, timeout=15)
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            logger.warning("youtube collector: failed to fetch region %s", region, exc_info=True)
            continue
        for video in payload.get("items", []):
            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})
            title = snippet.get("title")
            if not title:
                continue
            category_id = snippet.get("categoryId")
            if config.YOUTUBE_CATEGORY_IDS and category_id not in config.YOUTUBE_CATEGORY_IDS:
                continue
            view_count = float(statistics.get("viewCount", 0))
            items.append({
                "topic_key": base.normalize_key(title),
                "source": "youtube",
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video.get('id', '')}",
                "engagement": view_count / 1000,
                "engagement_type": "views_k",
                "region": region,
                "fetched_at": base.now_iso(),
                "content_created_at": snippet.get("publishedAt"),
            })
    return items
