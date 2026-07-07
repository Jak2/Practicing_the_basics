import pytest
from unittest.mock import MagicMock, patch
from core.config import get_config
from agents.trend_discovery import TrendDiscovery
from core.models import TopicResult

FIXTURE = "tests/fixtures/config_valid.yaml"


def make_config():
    return get_config(FIXTURE)


def test_run_returns_topic_results(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    mocker.patch("agents.trend_discovery.TavilyClient.search", return_value={
        "results": [
            {"title": "Gemini 2.0 is here", "content": "Google releases Gemini 2.0",
             "url": "https://example.com/gemini"}
        ]
    })
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results, source_results = agent.run(["generative-ai"], n_topics=1)

    assert len(results) == 1
    assert isinstance(results[0], TopicResult)
    assert results[0].source == "tavily"
    assert results[0].category == "generative-ai"


def test_run_deduplicates_by_title(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    duplicate = TopicResult(title="Same topic", summary="desc", source="reddit",
                             category="generative-ai", url="https://a.com")
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=[duplicate])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[duplicate])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results, _ = agent.run(["generative-ai"], n_topics=5)

    titles = [r.title for r in results]
    assert titles.count("Same topic") == 1


def test_run_respects_n_topics_limit(mocker):
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    many = [TopicResult(title=f"Topic {i}", summary="s", source="tavily",
                         category="generative-ai", url="https://x.com") for i in range(10)]
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=many)
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_hackernews", return_value=[])

    agent = TrendDiscovery(make_config())
    results, _ = agent.run(["generative-ai"], n_topics=3)
    assert len(results) == 3


def test_hackernews_error_surfaces_in_source_results(mocker):
    """_fetch_hackernews errors must propagate so run() records them as failed, not success."""
    mocker.patch.dict("os.environ", {"TAVILY_API_KEY": "fake", "REDDIT_CLIENT_ID": "x",
                                      "REDDIT_CLIENT_SECRET": "y", "REDDIT_USER_AGENT": "z"})
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_tavily", return_value=[])
    mocker.patch("agents.trend_discovery.TrendDiscovery._fetch_reddit", return_value=[])
    mocker.patch("agents.trend_discovery.httpx.get", side_effect=Exception("connection refused"))

    agent = TrendDiscovery(make_config())
    results, source_results = agent.run(["generative-ai"], n_topics=3)

    assert results == []
    assert source_results["hackernews"]["error"] is not None
    assert source_results["hackernews"]["error"] == "connection refused"
