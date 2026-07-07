#!/usr/bin/env bash
# Cron wrapper for run_daily.py. API keys come from .env (loaded automatically
# by trend_engine/config.py) — cron does not need its own copy of your shell's
# exported vars as long as .env exists next to this script.
cd "$(dirname "$0")"
mkdir -p output
/usr/bin/env python3 run_daily.py >> output/cron.log 2>&1
