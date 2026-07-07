"""Explainable virality scoring.

Engagement ranges differ wildly across sources (a top Reddit post has thousands of
upvotes, a top Civitai image a few hundred reactions), so raw numbers can't be ranked
together. Score = 100 * log1p(engagement) / log1p(max engagement within the same
source batch): log tames whales, per-source normalization makes cross-source ranking
fair. Pure function — no I/O.
"""
import math
from collections import defaultdict
from core.trend_models import TrendItem


def score_trends(items: list[TrendItem]) -> list[TrendItem]:
    if not items:
        return []

    max_by_source: dict[str, int] = defaultdict(int)
    for item in items:
        max_by_source[item.source] = max(max_by_source[item.source], item.engagement)

    for item in items:
        source_max = max_by_source[item.source]
        if source_max <= 0 or item.engagement <= 0:
            item.virality_score = 0.0
        else:
            item.virality_score = round(
                100 * math.log1p(item.engagement) / math.log1p(source_max), 1
            )

    return sorted(items, key=lambda t: (t.virality_score, t.engagement), reverse=True)
