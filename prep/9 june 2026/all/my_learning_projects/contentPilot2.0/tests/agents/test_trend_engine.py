from datetime import datetime, UTC
from unittest.mock import MagicMock
from core.trend_models import TrendItem, TrendInsight
from core.trend_store import load_trends
from agents.trend_engine import TrendEngine


def make_item(slug="x", source="reddit", engagement=10) -> TrendItem:
    return TrendItem(
        id=f"id-{slug}", prompt=f"prompt {slug}", source=source, kind="text",
        engagement=engagement, fetched_at=datetime.now(UTC),
    )


def test_run_fetches_scores_analyzes_and_stores(tmp_path, mocker):
    trends_path = str(tmp_path / "trends.json")
    run_log_path = str(tmp_path / "run_log.json")

    fake_source = MagicMock()
    fake_source.fetch.return_value = [make_item("a", engagement=100), make_item("b", engagement=10)]
    mocker.patch("agents.trend_engine.SOURCES", {"reddit": lambda: fake_source})

    fake_extractor = MagicMock()
    fake_extractor.extract.return_value = TrendInsight(pattern_tags=["t"], why_viral="Works. Well.", category="misc")
    mocker.patch("agents.trend_engine.InsightExtractor", return_value=fake_extractor)

    engine = TrendEngine(trends_path=trends_path, run_log_path=run_log_path)
    engine.run(sources=["reddit"], top=2)

    state = load_trends(trends_path)
    assert len(state.trends) == 2
    assert state.trends[0].virality_score == 100.0
    assert state.trends[0].insight is not None
    assert state.last_refreshed is not None


def test_one_source_failure_does_not_kill_run(tmp_path, mocker):
    trends_path = str(tmp_path / "trends.json")
    good = MagicMock()
    good.fetch.return_value = [make_item("ok", engagement=5)]
    bad = MagicMock()
    bad.fetch.side_effect = RuntimeError("api down")
    mocker.patch("agents.trend_engine.SOURCES", {"reddit": lambda: good, "civitai": lambda: bad})
    mocker.patch("agents.trend_engine.InsightExtractor", return_value=MagicMock(extract=MagicMock(return_value=None)))

    engine = TrendEngine(trends_path=trends_path, run_log_path=str(tmp_path / "rl.json"))
    engine.run(sources=["reddit", "civitai"], top=5)

    state = load_trends(trends_path)
    assert len(state.trends) == 1
    assert state.trends[0].id == "id-ok"


def test_insight_only_for_top_n(tmp_path, mocker):
    trends_path = str(tmp_path / "trends.json")
    src = MagicMock()
    src.fetch.return_value = [make_item(str(i), engagement=100 - i) for i in range(5)]
    mocker.patch("agents.trend_engine.SOURCES", {"reddit": lambda: src})
    extractor = MagicMock()
    extractor.extract.return_value = None
    mocker.patch("agents.trend_engine.InsightExtractor", return_value=extractor)

    engine = TrendEngine(trends_path=trends_path, run_log_path=str(tmp_path / "rl.json"))
    engine.run(sources=["reddit"], top=5, insight_top=2)

    assert extractor.extract.call_count == 2
