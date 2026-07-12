from datetime import datetime, UTC
from core.trend_models import TrendItem, TrendInsight, TrendState, trend_id


def make_item(**kw) -> TrendItem:
    base = dict(
        id="abc123def456", prompt="a cinematic portrait", source="civitai",
        kind="image", engagement=100, fetched_at=datetime.now(UTC),
    )
    base.update(kw)
    return TrendItem(**base)


def test_trend_id_deterministic():
    assert trend_id("civitai", "hello") == trend_id("civitai", "hello")
    assert trend_id("civitai", "hello") != trend_id("promptschat", "hello")
    assert len(trend_id("civitai", "hello")) == 12


def test_trend_item_defaults():
    item = make_item()
    assert item.virality_score == 0.0
    assert item.insight is None
    assert item.image_url is None
    assert item.source_url == ""


def test_trend_insight_attaches():
    ins = TrendInsight(pattern_tags=["negative prompt"], why_viral="It works. Very well.", category="portrait")
    item = make_item(insight=ins)
    assert item.insight.category == "portrait"


def test_trend_state_roundtrip_json():
    state = TrendState(trends=[make_item()], last_refreshed=datetime.now(UTC))
    loaded = TrendState.model_validate_json(state.model_dump_json())
    assert loaded == state
