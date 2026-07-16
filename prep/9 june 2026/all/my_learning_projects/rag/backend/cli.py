"""CLI: index a folder, then ask questions. Run: python -m backend.cli ..."""
import sys

from backend.config import get_config
from backend.indexing import index_folder
from backend.engine import ask


def main():
    cfg = get_config()
    if len(sys.argv) < 2:
        print('usage: python -m backend.cli [index [<folder>] | ask "<question>"]')
        return
    cmd = sys.argv[1]
    if cmd == "index":
        folder = sys.argv[2] if len(sys.argv) > 2 else cfg["corpus_dir"]
        stats = index_folder(folder, cfg)
        print(f"indexed: +{stats['added']} new, {stats['updated']} updated, {stats['skipped']} unchanged")
    elif cmd == "ask":
        res = ask(sys.argv[2], cfg)
        print(res["answer"])
        print("\nsources:", ", ".join(res["sources"]) or "(none)")
    else:
        print(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
