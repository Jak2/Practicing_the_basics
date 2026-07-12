import json
from unittest.mock import MagicMock
from agents.sources.civitai import CivitaiSource
from agents.sources.promptschat import PromptsChatSource

CIVITAI_FIXTURE = {
    "items": [
        {
            "id": 1, "url": "https://image.civitai.com/a.jpeg",
            "meta": {"prompt": "masterpiece, cinematic portrait of a warrior"},
            "stats": {"likeCount": 900, "heartCount": 100, "laughCount": 0, "cryCount": 0, "commentCount": 5},
        },
        {
            "id": 2, "url": "https://image.civitai.com/b.jpeg",
            "meta": None,  # hidden without auth token — must be skipped
            "stats": {"likeCount": 5000, "heartCount": 0, "laughCount": 0, "cryCount": 0, "commentCount": 0},
        },
    ]
}

PROMPTSCHAT_FIXTURE = {
    "rows": [
        {"row": {"act": "Ethereum Developer", "prompt": "Imagine you are an experienced dev...", "for_devs": True}},
        {"row": {"act": "Linux Terminal", "prompt": "I want you to act as a linux terminal...", "for_devs": True}},
    ],
    "num_rows_total": 1984,
}


def test_civitai_parses_items_and_skips_missing_prompts(mocker):
    resp = MagicMock(status_code=200)
    resp.json.return_value = CIVITAI_FIXTURE
    mocker.patch("agents.sources.civitai.httpx.get", return_value=resp)

    items = CivitaiSource().fetch(limit=10)

    assert len(items) == 1  # meta=None item skipped
    item = items[0]
    assert item.source == "civitai"
    assert item.kind == "image"
    assert item.prompt.startswith("masterpiece")
    assert item.engagement == 1000  # like 900 + heart 100
    assert item.image_url == "https://image.civitai.com/a.jpeg"
    assert item.source_url == "https://civitai.com/images/1"


def test_promptschat_parses_rows(mocker):
    resp = MagicMock(status_code=200)
    resp.json.return_value = PROMPTSCHAT_FIXTURE
    mocker.patch("agents.sources.promptschat.httpx.get", return_value=resp)

    items = PromptsChatSource().fetch(limit=2)

    assert len(items) == 2
    assert items[0].source == "promptschat"
    assert items[0].kind == "text"
    assert items[0].engagement == 0
    assert "Ethereum Developer" in items[0].prompt or items[0].prompt.startswith("Imagine")


