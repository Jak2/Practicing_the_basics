#!/usr/bin/env bash
# Start the app in the right order: ensure Ollama is up, index on first run, serve.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "No .venv found. Run ./install.sh first."
  exit 1
fi

# Load .env (simple KEY=value lines) so we know which LLM backend to prepare.
if [ -f .env ]; then
  set -a; . ./.env; set +a
fi
LLM="${RAG_LLM:-$(grep -E '^llm:' config.yaml | awk '{print $2}')}"

if [ "$LLM" = "ollama" ]; then
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama not installed. Run ./install.sh first."
    exit 1
  fi
  if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "==> starting Ollama..."
    nohup ollama serve >/dev/null 2>&1 &
    for _ in $(seq 1 30); do
      curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && break
      sleep 1
    done
  fi
fi

# Build the index on first run (no vector DB yet).
if [ ! -d .rag_db ]; then
  echo "==> indexing corpus (first run)..."
  ./.venv/bin/python -m backend.cli index
fi

echo "==> launching web GUI"
exec ./.venv/bin/python run.py
