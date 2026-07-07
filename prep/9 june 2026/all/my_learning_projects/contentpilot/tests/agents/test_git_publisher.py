import pytest
import git
from pathlib import Path
from core.config import get_config, Config
from agents.git_publisher import GitPublisher

FIXTURE = "tests/fixtures/config_valid.yaml"


@pytest.fixture
def git_repo(tmp_path):
    repo = git.Repo.init(tmp_path)
    repo.config_writer().set_value("user", "name", "Test").release()
    repo.config_writer().set_value("user", "email", "test@test.com").release()
    (tmp_path / "content" / "prompts").mkdir(parents=True)
    (tmp_path / "content" / "workflows").mkdir(parents=True)
    (tmp_path / "public" / "images").mkdir(parents=True)
    readme = tmp_path / "README.md"
    readme.write_text("# Test repo")
    repo.index.add(["README.md"])
    repo.index.commit("init")
    return tmp_path, repo


def make_config_for_repo(repo_path: str) -> Config:
    cfg = get_config(FIXTURE)
    cfg.target_repo = repo_path
    return cfg


def test_publish_prompt_creates_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    sha = publisher.publish("my-prompt", "---\ntitle: test\n---\nContent", "prompt")

    assert (repo_path / "content" / "prompts" / "my-prompt.md").exists()
    assert sha
    assert len(sha) >= 7


def test_publish_workflow_creates_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    sha = publisher.publish("my-workflow", "---\ntitle: wf\n---\n## Step 1\ncontent", "workflow")

    assert (repo_path / "content" / "workflows" / "my-workflow.md").exists()


def test_delete_removes_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    publisher.publish("del-me", "---\ntitle: del\n---\ncontent", "prompt")
    assert (repo_path / "content" / "prompts" / "del-me.md").exists()

    publisher.delete("del-me", "prompt")
    assert not (repo_path / "content" / "prompts" / "del-me.md").exists()


def test_repush_overwrites_file(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    publisher.publish("repush-me", "---\ntitle: old\n---\nOld content", "prompt")
    publisher.repush("repush-me", "---\ntitle: new\n---\nNew content", "prompt")

    content = (repo_path / "content" / "prompts" / "repush-me.md").read_text()
    assert "New content" in content


def test_publish_does_not_commit_unrelated_staged_changes(git_repo):
    """Regression test: publish() must only commit the file it just wrote,
    not sweep in other changes the caller happened to have staged."""
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    unrelated = repo_path / "unrelated.md"
    unrelated.write_text("unrelated change")
    repo.index.add(["unrelated.md"])

    publisher.publish("my-prompt", "---\ntitle: test\n---\nContent", "prompt")

    staged = repo.index.diff("HEAD")
    assert any(d.a_path == "unrelated.md" for d in staged), (
        "unrelated staged change should remain staged, untouched by publish()"
    )
    last_commit_files = repo.head.commit.stats.files.keys()
    assert "unrelated.md" not in last_commit_files
    assert any("my-prompt.md" in f for f in last_commit_files)


def test_publish_draft_true_writes_to_drafts_dir_not_target_repo(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    drafts_dir = tmp_path / "drafts"
    publisher = GitPublisher(cfg, drafts_dir=str(drafts_dir))

    commit_sha = publisher.publish("draft-post", "---\ntitle: d\n---\ncontent", "prompt", draft=True)

    assert commit_sha is None
    assert (drafts_dir / "content" / "prompts" / "draft-post.md").exists()
    assert not (repo_path / "content" / "prompts" / "draft-post.md").exists()
    assert repo.head.commit.message.strip() == "init"  # no new commit made


def test_publish_draft_promotes_file_commits_and_pushes(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    drafts_dir = tmp_path / "drafts"
    publisher = GitPublisher(cfg, drafts_dir=str(drafts_dir))
    publisher.publish("promote-me", "---\ntitle: p\n---\ncontent", "prompt", draft=True)

    commit_sha, push_status = publisher.publish_draft("promote-me", "prompt")

    assert (repo_path / "content" / "prompts" / "promote-me.md").exists()
    assert not (drafts_dir / "content" / "prompts" / "promote-me.md").exists()
    assert commit_sha
    assert push_status == "no_remote"  # git_repo fixture has no origin remote


def test_publish_draft_raises_if_no_draft_exists(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg, drafts_dir=str(tmp_path / "drafts"))

    with pytest.raises(FileNotFoundError):
        publisher.publish_draft("never-existed", "prompt")


def test_discard_draft_deletes_file_without_git_operation(git_repo, tmp_path):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    drafts_dir = tmp_path / "drafts"
    publisher = GitPublisher(cfg, drafts_dir=str(drafts_dir))
    publisher.publish("reject-me", "---\ntitle: r\n---\ncontent", "prompt", draft=True)

    publisher.discard_draft("reject-me", "prompt")

    assert not (drafts_dir / "content" / "prompts" / "reject-me.md").exists()
    assert repo.head.commit.message.strip() == "init"


def test_push_returns_no_remote_when_origin_missing(git_repo):
    repo_path, repo = git_repo
    cfg = make_config_for_repo(str(repo_path))
    publisher = GitPublisher(cfg)

    assert publisher.push() == "no_remote"
