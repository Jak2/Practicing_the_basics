import json
import pathlib
from unittest.mock import patch, MagicMock

from trend_engine.collectors import base, hackernews, reddit, youtube, wikipedia
from trend_engine import collectors

FIX = pathlib.Path(__file__).parent / "fixtures"

reddit.PACE_SECONDS = 0  # no inter-subreddit delay in mocked tests


def _resp(payload):
    m = MagicMock()
    m.json.return_value = payload
    m.raise_for_status.return_value = None
    return m


def _xml_resp(text):
    m = MagicMock()
    m.content = text.encode("utf-8")
    m.raise_for_status.return_value = None
    return m


def test_normalize_key():
    assert base.normalize_key("GPT-6  Leaked, Benchmarks!!") == "gpt 6 leaked benchmarks"


def test_epoch_to_iso():
    assert base.epoch_to_iso(1751400000) == "2025-07-01T20:00:00+00:00"
    assert base.epoch_to_iso(None) is None
    assert base.epoch_to_iso("not-a-number") is None


def test_hn_collect_maps_fields():
    ids = json.loads((FIX / "hn_top.json").read_text())
    item = json.loads((FIX / "hn_item.json").read_text())
    with patch("trend_engine.collectors.hackernews.requests.get",
               side_effect=[_resp(ids)] + [_resp(item)] * len(ids)):
        out = hackernews.collect()
    assert out and out[0]["source"] == "hackernews" and out[0]["engagement"] == 934
    assert out[0]["topic_key"] == "gpt 6 leaked benchmarks"
    assert out[0]["region"] == "GLOBAL"
    assert out[0]["engagement_type"] == "points"
    assert out[0]["content_created_at"] == "2025-07-01T20:00:00+00:00"


def test_hn_collect_partial_failure_keeps_good_items():
    ids = json.loads((FIX / "hn_top.json").read_text())
    item = json.loads((FIX / "hn_item.json").read_text())
    with patch(
        "trend_engine.collectors.hackernews.requests.get",
        side_effect=[_resp(ids), Exception("boom"), _resp(item)],
    ):
        out = hackernews.collect()
    assert len(out) == 1
    assert out[0]["source"] == "hackernews"


def test_hn_collect_error_swallow():
    with patch("trend_engine.collectors.hackernews.requests.get", side_effect=Exception("down")):
        assert hackernews.collect() == []


def test_reddit_collect_and_error_swallow():
    xml_text = (FIX / "reddit_hot.atom.xml").read_text()
    with patch("trend_engine.collectors.reddit.requests.get", return_value=_xml_resp(xml_text)):
        out = reddit.collect()
    assert out and out[0]["source"] == "reddit"
    assert out[0]["engagement"] == 100.0
    assert out[0]["engagement_type"] == "rank_proxy"
    assert out[0]["region"] == "GLOBAL"
    assert out[0]["content_created_at"] == "2026-07-01T18:30:00+00:00"
    with patch("trend_engine.collectors.reddit.requests.get", side_effect=Exception("down")):
        assert reddit.collect() == []


def test_reddit_india_region():
    xml_text = (FIX / "reddit_hot.atom.xml").read_text()
    with patch("trend_engine.collectors.reddit.requests.get", return_value=_xml_resp(xml_text)):
        out = reddit.collect()
    regions = {item["region"] for item in out}
    assert "IN" in regions


def test_reddit_user_agent_header():
    xml_text = (FIX / "reddit_hot.atom.xml").read_text()
    with patch("trend_engine.collectors.reddit.requests.get", return_value=_xml_resp(xml_text)) as mock_get:
        reddit.collect()
    for call in mock_get.call_args_list:
        headers = call.kwargs.get("headers", {})
        assert "User-Agent" in headers


def test_youtube_no_api_key_returns_empty(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    assert youtube.collect() == []


def test_youtube_collect_maps_fields(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    payload = json.loads((FIX / "yt_trending.json").read_text())
    with patch("trend_engine.collectors.youtube.requests.get", return_value=_resp(payload)):
        out = youtube.collect()
    assert out and out[0]["source"] == "youtube"
    assert out[0]["engagement"] == 1200000 / 1000
    assert out[0]["topic_key"] == "gpt 6 is insane"
    assert out[0]["content_created_at"] == "2026-07-01T10:00:00Z"


def test_youtube_error_swallow(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    with patch("trend_engine.collectors.youtube.requests.get", side_effect=Exception("down")):
        assert youtube.collect() == []


def test_youtube_filters_out_of_category_videos(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    payload = {"items": [
        {"id": "tech1", "snippet": {"title": "New AI chip", "categoryId": "28"},
         "statistics": {"viewCount": "1000"}},
        {"id": "music1", "snippet": {"title": "Pop hit music video", "categoryId": "10"},
         "statistics": {"viewCount": "9000000"}},
    ]}
    with patch("trend_engine.collectors.youtube.requests.get", return_value=_resp(payload)):
        out = youtube.collect()
    keys = [i["topic_key"] for i in out]
    assert "new ai chip" in keys
    assert "pop hit music video" not in keys


def test_wikipedia_collect_skips_boilerplate():
    payload = json.loads((FIX / "wiki_views.json").read_text())
    with patch("trend_engine.collectors.wikipedia.requests.get", return_value=_resp(payload)):
        out = wikipedia.collect()
    titles = [item["title"] for item in out]
    assert "Main_Page" not in titles
    assert not any(t.startswith("Special:") for t in titles)
    assert out and out[0]["source"] == "wikipedia"
    assert out[0]["engagement"] == 250000 / 1000


def test_wikipedia_title_display_form_underscores_to_spaces():
    payload = {"items": [{"articles": [{"article": "Elon_Musk", "views": 100000, "rank": 1}]}]}
    with patch("trend_engine.collectors.wikipedia.requests.get", return_value=_resp(payload)):
        out = wikipedia.collect()
    assert out[0]["title"] == "Elon Musk"
    assert out[0]["topic_key"] == base.normalize_key("Elon Musk")
    assert out[0]["url"] == "https://en.wikipedia.org/wiki/Elon_Musk"


def test_wikipedia_user_agent_header():
    payload = json.loads((FIX / "wiki_views.json").read_text())
    with patch("trend_engine.collectors.wikipedia.requests.get", return_value=_resp(payload)) as mock_get:
        wikipedia.collect()
    for call in mock_get.call_args_list:
        headers = call.kwargs.get("headers", {})
        assert "User-Agent" in headers
        assert headers["User-Agent"] == base.USER_AGENT


def test_wikipedia_error_swallow():
    with patch("trend_engine.collectors.wikipedia.requests.get", side_effect=Exception("down")):
        assert wikipedia.collect() == []


def test_fetched_at_is_timezone_aware():
    ids = json.loads((FIX / "hn_top.json").read_text())
    item = json.loads((FIX / "hn_item.json").read_text())
    with patch("trend_engine.collectors.hackernews.requests.get",
               side_effect=[_resp(ids)] + [_resp(item)] * len(ids)):
        out = hackernews.collect()
    import datetime as dt
    parsed = dt.datetime.fromisoformat(out[0]["fetched_at"])
    assert parsed.tzinfo is not None


def test_collectors_all_list():
    assert collectors.ALL == [hackernews, reddit, youtube, wikipedia]
