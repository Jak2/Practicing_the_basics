from pathlib import Path
from filelock import FileLock
from core.models import ManifestState, PostEntry

DEFAULT_PATH = "manifest.json"


def _lock_path(manifest_path: str) -> str:
    return manifest_path + ".lock"


def load_manifest(path: str = DEFAULT_PATH) -> ManifestState:
    p = Path(path)
    if not p.exists():
        return ManifestState()
    return ManifestState.model_validate_json(p.read_text())


def save_manifest(state: ManifestState, path: str = DEFAULT_PATH) -> None:
    Path(path).write_text(state.model_dump_json(indent=2))


def append_post(post: PostEntry, path: str = DEFAULT_PATH) -> None:
    with FileLock(_lock_path(path)):
        state = load_manifest(path)
        state.posts.append(post)
        save_manifest(state, path)


def update_post_status(
    slug: str,
    status: str,
    push_status: str | None = None,
    git_commit: str | None = None,
    path: str = DEFAULT_PATH,
) -> None:
    with FileLock(_lock_path(path)):
        state = load_manifest(path)
        for post in state.posts:
            if post.slug == slug:
                post.status = status
                if push_status is not None:
                    post.push_status = push_status
                if git_commit is not None:
                    post.git_commit = git_commit
                save_manifest(state, path)
                return
        raise ValueError(f"No post found with slug '{slug}'")


def delete_post(slug: str, path: str = DEFAULT_PATH) -> None:
    with FileLock(_lock_path(path)):
        state = load_manifest(path)
        state.posts = [p for p in state.posts if p.slug != slug]
        save_manifest(state, path)
