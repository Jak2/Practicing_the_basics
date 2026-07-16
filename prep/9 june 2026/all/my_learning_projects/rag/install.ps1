# Zero-fuss setup for Windows: Python venv + deps + Ollama + default model.
# Run in PowerShell:  .\install.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$model = if ($env:RAG_OLLAMA_MODEL) { $env:RAG_OLLAMA_MODEL } else { "qwen2.5:1.5b" }

Write-Host "==> 1/4  Python virtual environment (.venv)"
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\python -m pip install --upgrade pip | Out-Null
& .\.venv\Scripts\python -m pip install -r requirements.txt

Write-Host "==> 2/4  Ollama"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  Write-Host "    installing Ollama..."
  try {
    winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
  } catch {
    Write-Host "    winget unavailable — download the installer from https://ollama.com/download and re-run this script."
    exit 1
  }
  $env:Path += ";$env:LOCALAPPDATA\Programs\Ollama"
} else {
  Write-Host "    already installed"
}

Write-Host "==> 3/4  Start Ollama and pull '$model'"
if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
  Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
  Start-Sleep -Seconds 3
}
ollama pull $model

Write-Host "==> 4/4  Config (.env)"
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "    created .env from template"
} else {
  Write-Host "    .env already exists — left untouched"
}

Write-Host ""
Write-Host "Setup complete. Start the app with:  .\run.ps1"
