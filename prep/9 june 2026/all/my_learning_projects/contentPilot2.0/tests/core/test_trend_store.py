from datetime import datetime, UTC
from core.trend_models import TrendItem, TrendState
from core.trend_store import load_trends, save_trends, delete_trend


def make_item(slug="x", source="reddit") -> TrendItem:
    return TrendItem(
        id=f"id-{slug}", prompt=f"prompt {slug}", source=source, kind="text",
        engagement=10, fetched_at=datetime.now(UTC),
    )


def test_load_trends_missing_file_returns_empty(tmp_path):
    state = load_trends(str(tmp_path / "trends.json"))
    assert state.trends == []
    assert state.last_refreshed is None


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / "trends.json")
    state = TrendState(trends=[make_item("a"), make_item("b")], last_refreshed=datetime.now(UTC))
    save_trends(state, path)
    assert load_trends(path) == state


def test_delete_trend_removes_by_id(tmp_path):
    path = str(tmp_path / "trends.json")
    save_trends(TrendState(trends=[make_item("a"), make_item("b")]), path)

    delete_trend("id-a", path)

    remaining = load_trends(path).trends
    assert [t.id for t in remaining] == ["id-b"]
