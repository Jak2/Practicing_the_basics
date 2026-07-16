# Start the app in the right order: ensure Ollama is up, index on first run, serve.
# Run in PowerShell:  .\run.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
  Write-Host "No .venv found. Run .\install.ps1 first."
  exit 1
}

# Which LLM backend? .env RAG_LLM overrides config.yaml.
$llm = (Select-String -Path config.yaml -Pattern '^llm:\s*(\S+)').Matches.Groups[1].Value
if (Test-Path .env) {
  $m = Select-String -Path .env -Pattern '^\s*RAG_LLM\s*=\s*(\S+)'
  if ($m) { $llm = $m.Matches.Groups[1].Value }
}

if ($llm -eq "ollama") {
  if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama not installed. Run .\install.ps1 first."
    exit 1
  }
  if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
    Write-Host "==> starting Ollama..."
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
  }
}

if (-not (Test-Path .rag_db)) {
  Write-Host "==> indexing corpus (first run)..."
  & .\.venv\Scripts\python -m backend.cli index
}

Write-Host "==> launching web GUI"
& .\.venv\Scripts\python run.py
