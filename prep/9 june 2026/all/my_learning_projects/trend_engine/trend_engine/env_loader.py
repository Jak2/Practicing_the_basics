"""Minimal stdlib .env loader — no python-dotenv dependency.

Reads KEY=VALUE lines from a .env file at the repo root and populates
os.environ, WITHOUT overwriting variables already exported in the shell
(so `export ANTHROPIC_API_KEY=...` always wins over .env, matching normal
dotenv semantics). Safe to call more than once; safe if .env doesn't exist.
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"


def load_env(path=ENV_PATH):
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
