import json, pathlib
from unittest.mock import patch
import run_daily
from trend_engine import config
from tests.test_store import _item

def test_collect_all_respects_source_enabled(monkeypatch):
    monkeypatch.setitem(config.SOURCE_ENABLED, "hackernews", False)
    called = []
    for name in ("hackernews", "reddit", "youtube", "wikipedia"):
        monkeypatch.setattr(f"trend_engine.collectors.{name}.collect",
                             lambda n=name: called.append(n) or [])
    run_daily.collect_all()
    assert "hackernews" not in called
    assert set(called) == {"reddit", "youtube", "wikipedia"}

def test_full_pipeline(tmp_path):
    fake_items = [_item(topic="ai everywhere", eng=999), _item(topic="ai everywhere", eng=500, source="reddit")]
    llm = json.dumps({"topics": [{"canonical_key": "ai everywhere", "merged_keys": [],
        "explanation": "AI is everywhere today.", "category": "AI",
        "platform_fit": "short-video", "stage": "peaking"}]})
    with patch("run_daily.collect_all", return_value=fake_items), \
         patch("trend_engine.enrich._call_llm", return_value=llm):
        code = run_daily.main(db_path=tmp_path / "t.db", out_root=tmp_path / "out")
    assert code == 0
    days = list((tmp_path / "out").iterdir())
    assert any((d / "top100.html").exists() for d in days if d.is_dir())

def test_exit_1_when_nothing_collected(tmp_path):
    with patch("run_daily.collect_all", return_value=[]):
        assert run_daily.main(db_path=tmp_path / "t.db", out_root=tmp_path / "out") == 1
