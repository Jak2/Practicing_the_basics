import json
from unittest.mock import MagicMock
from agents.sources.civitai import CivitaiSource
from agents.sources.promptschat import PromptsChatSource
from agents.sources.reddit_trends import RedditTrendsSource

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


def test_reddit_parses_text_and_image_posts(mocker):
    text_post = MagicMock(
        title="My mega prompt", selftext="Act as a career coach and...",
        score=420, permalink="/r/ChatGPTPromptGenius/1", url="https://reddit.com/x",
    )
    image_post = MagicMock(
        title="cinematic portrait, 85mm, volumetric light", selftext="",
        score=2100, permalink="/r/StableDiffusion/2", url="https://i.redd.it/pic.jpg",
    )
    sub = MagicMock()
    sub.top.return_value = [text_post]
    img_sub = MagicMock()
    img_sub.top.return_value = [image_post]
    reddit = MagicMock()
    reddit.subreddit.side_effect = lambda name: img_sub if name in ("StableDiffusion", "midjourney") else sub
    mocker.patch("agents.sources.reddit_trends.praw.Reddit", return_value=reddit)

    items = RedditTrendsSource().fetch(limit=5)

    kinds = {i.kind for i in items}
    assert "text" in kinds and "image" in kinds
    img = next(i for i in items if i.kind == "image")
    assert img.image_url == "https://i.redd.it/pic.jpg"
    assert img.engagement == 2100
    txt = next(i for i in items if i.kind == "text")
    assert txt.prompt.startswith("Act as a career coach")
