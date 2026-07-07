import pytest
from datetime import datetime
from core.models import TopicResult, PostEntry, ManifestState


def test_topic_result_valid():
    t = TopicResult(
        title="GPT-5 release",
        summary="OpenAI releases GPT-5",
        source="tavily",
        category="generative-ai",
        url="https://example.com",
    )
    assert t.title == "GPT-5 release"
    assert t.source == "tavily"


def test_topic_result_invalid_source():
    with pytest.raises(Exception):
        TopicResult(
            title="x", summary="x", source="invalid", category="x", url="x"
        )


def test_post_entry_defaults():
    p = PostEntry(
        slug="email-copy",
        title="Email Copy",
        type="prompt",
        category="generative-ai",
        topic="AI email trends",
        status="published",
        created_at=datetime.utcnow(),
        file_path="content/prompts/email-copy.md",
        source_url="https://reddit.com/r/ai",
    )
    assert p.image_path is None
    assert p.git_commit is None
    assert p.status == "published"


def test_post_entry_invalid_type():
    with pytest.raises(Exception):
        PostEntry(
            slug="x", title="x", type="invalid", category="x",
            topic="x", status="published", created_at=datetime.utcnow(),
            file_path="x", source_url="x",
        )


def test_manifest_state_empty():
    m = ManifestState()
    assert m.posts == []


def test_manifest_state_with_posts():
    p = PostEntry(
        slug="s", title="t", type="workflow", category="c",
        topic="tp", status="published", created_at=datetime.utcnow(),
        file_path="f", source_url="u",
    )
    m = ManifestState(posts=[p])
    assert len(m.posts) == 1
    assert m.posts[0].slug == "s"


from core.models import ScheduleConfig


def test_schedule_config_defaults():
    cfg = ScheduleConfig()
    assert cfg.enabled is False
    assert cfg.interval_hours == 24
    assert cfg.topics == 3
    assert cfg.prompts == 1
    assert cfg.workflows == 1
    assert cfg.categories == ["all"]
    assert cfg.publish is False


def test_schedule_config_custom_values():
    cfg = ScheduleConfig(enabled=True, interval_hours=6, topics=5, categories=["generative-ai"])
    assert cfg.enabled is True
    assert cfg.interval_hours == 6
    assert cfg.categories == ["generative-ai"]


def test_post_entry_push_status_defaults_to_none():
    p = PostEntry(
        slug="s", title="t", type="prompt", category="c", topic="tp",
        status="draft", created_at=datetime.utcnow(), file_path="x.md",
        source_url="http://x",
    )
    assert p.push_status is None


def test_post_entry_push_status_accepts_literal_values():
    p = PostEntry(
        slug="s", title="t", type="prompt", category="c", topic="tp",
        status="published", created_at=datetime.utcnow(), file_path="x.md",
        source_url="http://x", push_status="pushed",
    )
    assert p.push_status == "pushed"


def test_post_entry_migrates_legacy_pushed_status():
    p = PostEntry(
        slug="s", title="t", type="prompt", category="c", topic="tp",
        status="pushed", created_at=datetime.utcnow(), file_path="x.md",
        source_url="http://x",
    )
    assert p.status == "published"
