import logging
import time
import xml.etree.ElementTree as ET

import requests

from . import base
from .. import config

logger = logging.getLogger(__name__)

HOT_URL = "https://www.reddit.com/r/{sub}/hot.rss?limit=25"
PACE_SECONDS = 10  # delay between subreddit fetches; tests set this to 0
INDIA_SUBS = {"india", "developersindia"}
ATOM_NS = "{http://www.w3.org/2005/Atom}"


@base.safe_collect
def collect(session=None):
    getter = session.get if session is not None else requests.get
    headers = {"User-Agent": base.USER_AGENT}

    items = []
    for sub_index, sub in enumerate(config.SUBREDDITS):
        try:
            if sub_index and PACE_SECONDS:
                # reddit 429s rapid-fire RSS requests; pace consecutive fetches
                time.sleep(PACE_SECONDS)
            resp = getter(HOT_URL.format(sub=sub), headers=headers, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception:
            logger.warning("reddit collector: failed to fetch r/%s", sub, exc_info=True)
            continue
        region = "IN" if sub.lower() in INDIA_SUBS else "GLOBAL"
        entries = root.findall(f"{ATOM_NS}entry")
        for rank, entry in enumerate(entries):
            title_el = entry.find(f"{ATOM_NS}title")
            link_el = entry.find(f"{ATOM_NS}link")
            updated_el = entry.find(f"{ATOM_NS}updated")
            title = title_el.text if title_el is not None else None
            if not title:
                continue
            url = link_el.get("href") if link_el is not None else ""
            engagement = float(max(4, 100 - 4 * rank))
            items.append({
                "topic_key": base.normalize_key(title),
                "source": "reddit",
                "title": title,
                "url": url,
                "engagement": engagement,
                "engagement_type": "rank_proxy",
                "region": region,
                "fetched_at": base.now_iso(),
                "content_created_at": updated_el.text if updated_el is not None else None,
            })
    return items
