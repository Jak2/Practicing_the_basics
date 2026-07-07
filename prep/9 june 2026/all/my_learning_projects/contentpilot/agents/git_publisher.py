import shutil
from typing import Literal
from pathlib import Path
import git
from core.config import Config

DEFAULT_DRAFTS_DIR = "drafts"


class GitPublisher:
    def __init__(self, config: Config, drafts_dir: str = DEFAULT_DRAFTS_DIR):
        self.config = config
        self.repo = git.Repo(config.target_repo)
        self.drafts_dir = Path(drafts_dir)

    def _path_for(self, slug: str, post_type: Literal["prompt", "workflow"], base: Path) -> Path:
        if post_type == "prompt":
            return base / self.config.content_paths.prompts / f"{slug}.md"
        return base / self.config.content_paths.workflows / f"{slug}.md"

    def publish(
        self,
        slug: str,
        content: str,
        post_type: Literal["prompt", "workflow"],
        draft: bool = False,
    ) -> str | None:
        if draft:
            path = self._path_for(slug, post_type, self.drafts_dir)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return None

        base = Path(self.config.target_repo)
        path = self._path_for(slug, post_type, base)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        rel = str(path.relative_to(base))
        self.repo.git.add(rel)
        # Pathspec-scoped commit: only commits changes to `rel`, leaving any
        # other staged changes in the repo untouched (index.commit() would
        # have committed the whole index, sweeping in unrelated staged work).
        self.repo.git.commit("-m", f"content: add {post_type} '{slug}'", "--", rel)
        return self.repo.head.commit.hexsha[:7]

    def publish_draft(
        self,
        slug: str,
        post_type: Literal["prompt", "workflow"],
        image_rel_path: str | None = None,
    ) -> tuple[str, str]:
        draft_path = self._path_for(slug, post_type, self.drafts_dir)
        if not draft_path.exists():
            raise FileNotFoundError(f"No draft found for slug '{slug}'")

        content = draft_path.read_text(encoding="utf-8")
        commit_sha = self.publish(slug, content, post_type, draft=False)
        draft_path.unlink()

        if image_rel_path:
            draft_image = self.drafts_dir / image_rel_path
            if draft_image.exists():
                target_image = Path(self.config.target_repo) / image_rel_path
                target_image.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(draft_image), str(target_image))

        push_status = self.push()
        return commit_sha, push_status

    def discard_draft(self, slug: str, post_type: Literal["prompt", "workflow"]) -> None:
        path = self._path_for(slug, post_type, self.drafts_dir)
        if path.exists():
            path.unlink()

    def delete(self, slug: str, post_type: Literal["prompt", "workflow"]) -> str:
        path = self._path_for(slug, post_type, Path(self.config.target_repo))
        rel = str(path.relative_to(self.config.target_repo))
        self.repo.git.rm(rel)
        self.repo.git.commit("-m", f"content: remove {post_type} '{slug}'", "--", rel)
        return self.repo.head.commit.hexsha[:7]

    def repush(self, slug: str, content: str, post_type: Literal["prompt", "workflow"]) -> str:
        return self.publish(slug, content, post_type)

    def push(self) -> str:
        try:
            origin = self.repo.remotes["origin"]
        except IndexError:
            return "no_remote"
        try:
            origin.push()
            return "pushed"
        except git.exc.GitCommandError as e:
            import sys
            print(f"[ContentPilot] Warning: could not push to remote — {e}", file=sys.stderr)
            return "failed"
