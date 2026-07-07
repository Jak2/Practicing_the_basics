import html
import json

PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ background: #0f1117; color: #e6e6e6; font-family: system-ui, sans-serif; padding: 2rem; }}
h1, h2 {{ color: #7dd3fc; }}
.banner {{ background: #7f1d1d; color: #fecaca; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }}
.row {{ border-bottom: 1px solid #262b36; padding: 0.75rem 0; }}
.rank {{ color: #fbbf24; font-weight: bold; margin-right: 0.5rem; }}
.score {{ color: #fbbf24; }}
.badge {{ background: #1e293b; color: #7dd3fc; padding: 0.1rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem; }}
.explanation {{ color: #9ca3af; margin-top: 0.25rem; }}
a {{ color: #e6e6e6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.hint {{ color: #7dd3fc; font-style: italic; }}
</style>
</head>
<body>
<h1>{heading}</h1>
{banner}
{body}
</body>
</html>
"""

DEGRADED_BANNER = (
    '<div class="banner">&#9888; Degraded run &mdash; math-only rankings, '
    "no LLM enrichment.</div>"
)

PLATFORM_FILTERS = {
    "youtube": {"short-video", "long-form"},
    "instagram": {"short-video"},
    "x": {"thread"},
}

PLATFORM_HINTS = {
    "youtube": "Shorts angle: hook with the explanation line",
    "instagram": "Reels angle: trending-audio hook, explanation line as on-screen text",
    "x": "Thread starter: post the explanation as the hook tweet",
}


def _safe_url(url):
    """Return html-escaped url if it starts with http:// or https://, else return '#'."""
    if url and str(url).lower().startswith(("http://", "https://")):
        return html.escape(str(url))
    return "#"


def _topic_row(rank, topic):
    title = html.escape(str(topic.get("title", "")))
    explanation = html.escape(str(topic.get("explanation", "")))
    category = html.escape(str(topic.get("category", "")))
    stage = html.escape(str(topic.get("stage", "")))
    score = float(topic.get("score", 0) or 0)
    urls = topic.get("urls") or []
    url = _safe_url(urls[0]) if urls else "#"
    return (
        '<div class="row">'
        f'<span class="rank">#{rank}</span>'
        f'<a href="{url}">{title}</a>'
        f'<span class="score"> ({score:.2f})</span>'
        f'<span class="badge">{stage}</span>'
        f'<span class="badge">{category}</span>'
        f'<div class="explanation">{explanation}</div>'
        "</div>"
    )


def _top100_html(topics, enriched, run_date):
    banner = DEGRADED_BANNER if not enriched else ""
    body = "\n".join(_topic_row(i, t) for i, t in enumerate(topics, start=1))
    return PAGE_TEMPLATE.format(
        title=f"Top 100 - {run_date}",
        heading=f"Top 100 Trends &mdash; {run_date}",
        banner=banner,
        body=body,
    )


def _brief_html(platform, topics, run_date, enriched=True):
    fits = PLATFORM_FILTERS[platform]
    filtered = [t for t in topics if t.get("platform_fit") in fits]
    hint = html.escape(PLATFORM_HINTS[platform])
    rows = []
    for i, t in enumerate(filtered, start=1):
        rows.append(_topic_row(i, t) + f'<div class="hint">{hint}</div>')
    body = "\n".join(rows)
    banner = DEGRADED_BANNER if not enriched else ""
    return PAGE_TEMPLATE.format(
        title=f"{platform.title()} Brief - {run_date}",
        heading=f"{platform.title()} Brief &mdash; {run_date}",
        banner=banner,
        body=body,
    )


def publish(topics, enriched, run_date, out_root):
    day_dir = out_root / run_date
    briefs_dir = day_dir / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)

    (day_dir / "top100.html").write_text(_top100_html(topics, enriched, run_date))
    (day_dir / "top100.json").write_text(
        json.dumps({"run_date": run_date, "enriched": enriched, "topics": topics}, indent=2)
    )

    for platform in PLATFORM_FILTERS:
        (briefs_dir / f"{platform}.html").write_text(_brief_html(platform, topics, run_date, enriched))

    return day_dir


def save_to_db(conn, topics, run_date):
    rows = [
        (
            run_date,
            rank,
            t.get("topic_key"),
            t.get("title"),
            t.get("score"),
            t.get("explanation"),
            t.get("category"),
            t.get("platform_fit"),
            t.get("stage"),
            json.dumps(t.get("urls") or []),
        )
        for rank, t in enumerate(topics, start=1)
    ]
    conn.execute("DELETE FROM daily_top100 WHERE run_date = ?", (run_date,))
    conn.executemany(
        "INSERT INTO daily_top100 (run_date, rank, topic_key, title, score, explanation,"
        " category, platform_fit, stage, urls) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
