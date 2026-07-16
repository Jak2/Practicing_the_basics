#!/usr/bin/env bash
# Zero-fuss setup for Linux / macOS: Python venv + deps + Ollama + default model.
set -euo pipefail
cd "$(dirname "$0")"

MODEL="${RAG_OLLAMA_MODEL:-qwen2.5:1.5b}"
PY="${PYTHON:-python3}"

echo "==> 1/4  Python virtual environment (.venv)"
if [ ! -d .venv ]; then
  "$PY" -m venv .venv
fi
./.venv/bin/python -m pip install --upgrade pip >/dev/null
./.venv/bin/python -m pip install -r requirements.txt

echo "==> 2/4  Ollama"
if ! command -v ollama >/dev/null 2>&1; then
  echo "    installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "    already installed"
fi

echo "==> 3/4  Start Ollama and pull '$MODEL'"
if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve >/dev/null 2>&1 &
  for _ in $(seq 1 30); do
    curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && break
    sleep 1
  done
fi
ollama pull "$MODEL"

echo "==> 4/4  Config (.env)"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    created .env from template"
else
  echo "    .env already exists — left untouched"
fi

echo ""
echo "Setup complete. Start the app with:  ./run.sh"
