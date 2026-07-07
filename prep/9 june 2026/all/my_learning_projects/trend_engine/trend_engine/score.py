import re
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
    title_lower = title.lower()
    w = 1.0
    if any(re.search(rf"\b{re.escape(k)}\b", title_lower) for k in config.NICHE_AI_KEYWORDS):
        w *= 1.5
    if any(re.search(rf"\b{re.escape(k)}\b", title_lower) for k in config.NICHE_INDIA_KEYWORDS):
        w *= 1.3
    # Example third niche category — pair with config.NICHE_FINANCE_KEYWORDS.
    # if any(re.search(rf"\b{re.escape(k)}\b", title_lower) for k in config.NICHE_FINANCE_KEYWORDS):
    #     w *= 1.4
    return w

def is_excluded(title):
    title_lower = title.lower()
    return any(re.search(rf"\b{re.escape(k)}\b", title_lower) for k in config.EXCLUDE_KEYWORDS)

def _engagement_percentile(engagement, all_engagements):
    if not all_engagements:
        return 0.0
    n_le = sum(1 for e in all_engagements if e <= engagement)
    return n_le / len(all_engagements)

def rank_topics(conn, limit=150):
    topics = [t for t in store.todays_topics(conn) if not is_excluded(t["title"])]
    if not topics:
        return []
    histories = {t["topic_key"]: store.topic_history(conn, t["topic_key"]) for t in topics}
    zs = {t["topic_key"]: zscore(t["engagement"], histories[t["topic_key"]]) for t in topics}
    has_history_zs = [zs[k] for k, h in histories.items() if h]
    zmax = max(max(has_history_zs), EPS) if has_history_zs else EPS
    all_engagements = [t["engagement"] for t in topics]
    for t in topics:
        if histories[t["topic_key"]]:
            z_norm = max(zs[t["topic_key"]], 0) / zmax
        else:
            z_norm = _engagement_percentile(t["engagement"], all_engagements)
        d = decay(t["first_seen_hours"])
        t["score"] = z_norm * (0.5 + 0.5 * d) * corroboration(len(t["sources"])) * niche_weight(t["title"])
    return sorted(topics, key=lambda t: t["score"], reverse=True)[:limit]
