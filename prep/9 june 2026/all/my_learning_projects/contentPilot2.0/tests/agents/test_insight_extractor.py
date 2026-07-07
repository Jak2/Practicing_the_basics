import json
from datetime import datetime, UTC
from unittest.mock import MagicMock
from core.trend_models import TrendItem
from agents.insight_extractor import InsightExtractor


def make_item(prompt="cinematic portrait, 85mm") -> TrendItem:
    return TrendItem(
        id="abc", prompt=prompt, source="reddit", kind="image",
        engagement=100, fetched_at=datetime.now(UTC),
    )


def make_extractor(mocker, reply: str) -> InsightExtractor:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=reply)
    mocker.patch("agents.insight_extractor.ChatGoogleGenerativeAI", return_value=mock_llm)
    return InsightExtractor()


def test_extract_parses_valid_json(mocker):
    reply = json.dumps({
        "pattern_tags": ["lens spec", "cinematic style"],
        "why_viral": "Concrete lens tokens. Strong visual identity.",
        "category": "portrait",
    })
    extractor = make_extractor(mocker, reply)

    insight = extractor.extract(make_item())

    assert insight is not None
    assert insight.category == "portrait"
    assert "lens spec" in insight.pattern_tags


def test_extract_strips_markdown_fences(mocker):
    reply = '```json\n{"pattern_tags": ["a"], "why_viral": "b.", "category": "c"}\n```'
    extractor = make_extractor(mocker, reply)
    insight = extractor.extract(make_item())
    assert insight is not None
    assert insight.category == "c"


def test_extract_returns_none_on_garbage(mocker):
    extractor = make_extractor(mocker, "sorry, I can't do JSON today")
    assert extractor.extract(make_item()) is None


def test_extract_returns_none_on_api_error(mocker):
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("quota exceeded")
    mocker.patch("agents.insight_extractor.ChatGoogleGenerativeAI", return_value=mock_llm)
    extractor = InsightExtractor()
    assert extractor.extract(make_item()) is None
