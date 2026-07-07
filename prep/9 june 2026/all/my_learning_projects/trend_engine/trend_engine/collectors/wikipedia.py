import datetime as dt

import requests

from . import base

PAGEVIEWS_URL = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{y}/{m}/{d}"
)


def _is_boilerplate(article: str) -> bool:
    return article == "Main_Page" or article.startswith("Special:")


@base.safe_collect
def collect(session=None):
    getter = session.get if session is not None else requests.get

    yesterday = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)
    url = PAGEVIEWS_URL.format(y=yesterday.year, m=f"{yesterday.month:02d}", d=f"{yesterday.day:02d}")
    headers = {"User-Agent": base.USER_AGENT}
    resp = getter(url, headers=headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    items = []
    for entry in payload.get("items", []):
        for article in entry.get("articles", []):
            title = article.get("article", "")
            if not title or _is_boilerplate(title):
                continue
            views = float(article.get("views", 0))
            display_title = title.replace("_", " ")
            items.append({
                "topic_key": base.normalize_key(display_title),
                "source": "wikipedia",
                "title": display_title,
                "url": f"https://en.wikipedia.org/wiki/{title}",
                "engagement": views / 1000,
                "engagement_type": "views_k",
                "region": "GLOBAL",
                "fetched_at": base.now_iso(),
            })
    return items
