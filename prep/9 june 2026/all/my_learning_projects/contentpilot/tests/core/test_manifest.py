import json
import pytest
from datetime import datetime
from pathlib import Path
from core.manifest import load_manifest, save_manifest, append_post, delete_post, update_post_status
from core.models import ManifestState, PostEntry


def make_post(slug: str = "test-slug", post_type: str = "prompt") -> PostEntry:
    return PostEntry(
        slug=slug,
        title="Test Post",
        type=post_type,
        category="generative-ai",
        topic="AI trends",
        status="published",
        created_at=datetime.utcnow(),
        file_path=f"content/prompts/{slug}.md",
        source_url="https://example.com",
    )


def test_load_manifest_missing_file(tmp_path):
    state = load_manifest(str(tmp_path / "missing.json"))
    assert state.posts == []


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "manifest.json")
    post = make_post()
    state = ManifestState(posts=[post])
    save_manifest(state, path)
    loaded = load_manifest(path)
    assert len(loaded.posts) == 1
    assert loaded.posts[0].slug == "test-slug"


def test_append_post(tmp_path):
    path = str(tmp_path / "manifest.json")
    append_post(make_post("post-1"), path)
    append_post(make_post("post-2"), path)
    state = load_manifest(path)
    assert len(state.posts) == 2
    assert state.posts[1].slug == "post-2"


def test_delete_post(tmp_path):
    path = str(tmp_path / "manifest.json")
    append_post(make_post("keep-me"), path)
    append_post(make_post("delete-me"), path)
    delete_post("delete-me", path)
    state = load_manifest(path)
    assert len(state.posts) == 1
    assert state.posts[0].slug == "keep-me"


def test_update_post_status_changes_status_and_push_status(tmp_path):
    path = str(tmp_path / "manifest.json")
    post = PostEntry(
        slug="my-draft", title="t", type="prompt", category="c", topic="tp",
        status="draft", created_at=datetime.utcnow(), file_path="drafts/my-draft.md",
        source_url="http://x",
    )
    append_post(post, path)

    update_post_status("my-draft", status="published", push_status="pushed", git_commit="abc1234", path=path)

    state = load_manifest(path)
    updated = next(p for p in state.posts if p.slug == "my-draft")
    assert updated.status == "published"
    assert updated.push_status == "pushed"
    assert updated.git_commit == "abc1234"


def test_update_post_status_raises_for_unknown_slug(tmp_path):
    path = str(tmp_path / "manifest.json")
    with pytest.raises(ValueError):
        update_post_status("does-not-exist", status="published", path=path)
