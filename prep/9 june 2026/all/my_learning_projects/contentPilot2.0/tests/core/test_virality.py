from datetime import datetime, UTC
from core.trend_models import TrendItem
from core.virality import score_trends


def make_item(source="reddit", engagement=0, slug="x") -> TrendItem:
    return TrendItem(
        id=f"id-{source}-{slug}", prompt=f"p {slug}", source=source, kind="text",
        engagement=engagement, fetched_at=datetime.now(UTC),
    )


def test_top_item_per_source_scores_100():
    items = [make_item(engagement=500, slug="a"), make_item(engagement=50, slug="b")]
    scored = score_trends(items)
    assert scored[0].virality_score == 100.0
    assert scored[0].engagement == 500


def test_scores_sorted_descending():
    items = [make_item(engagement=e, slug=str(e)) for e in (5, 500, 50)]
    scored = score_trends(items)
    assert [t.engagement for t in scored] == [500, 50, 5]
    assert scored[0].virality_score >= scored[1].virality_score >= scored[2].virality_score


def test_per_source_normalization_makes_cross_source_fair():
    # reddit whale 5000 upvotes, civitai top 300 reactions — both are their source's max
    items = [
        make_item(source="reddit", engagement=5000, slug="r"),
        make_item(source="civitai", engagement=300, slug="c"),
    ]
    scored = score_trends(items)
    assert scored[0].virality_score == 100.0
    assert scored[1].virality_score == 100.0


def test_zero_engagement_scores_zero():
    items = [make_item(engagement=0, slug="z"), make_item(engagement=10, slug="t")]
    scored = score_trends(items)
    assert scored[-1].virality_score == 0.0


def test_empty_input_returns_empty():
    assert score_trends([]) == []
