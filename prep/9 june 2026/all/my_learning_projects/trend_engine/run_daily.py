import datetime as dt
import sys
import time

from trend_engine import collectors, config, enrich, publish, score, store


def collect_all():
    """Run every enabled collector in trend_engine.collectors.ALL and concatenate results.

    Collectors never raise out of collect() (they log and return [] on error),
    so no error handling is needed here. Toggle sources via config.SOURCE_ENABLED.
    """
    items = []
    for module in collectors.ALL:
        name = module.__name__.rsplit(".", 1)[-1]
        if not config.SOURCE_ENABLED.get(name, True):
            continue
        items.extend(module.collect())
    return items


def main(db_path=config.DB_PATH, out_root=config.OUTPUT_DIR):
    start = time.monotonic()
    run_date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    items = collect_all()
    if not items:
        _log_run(out_root, run_date, 0, 0, False, time.monotonic() - start)
        return 1

    conn = store.connect(db_path)
    try:
        store.insert_items(conn, items)

        candidates = score.rank_topics(conn, limit=150)
        topics, enriched = enrich.enrich(candidates)

        publish.publish(topics, enriched, run_date, out_root)
        publish.save_to_db(conn, topics, run_date)
    except Exception:
        # keep the one-row-per-run log contract even when a stage crashes
        _log_run(out_root, run_date, len(items), 0, False, time.monotonic() - start)
        raise
    finally:
        conn.close()

    duration_s = time.monotonic() - start
    _log_run(out_root, run_date, len(items), len(topics), enriched, duration_s)
    return 0


def _log_run(out_root, run_date, num_items, num_topics, enriched, duration_s):
    out_root.mkdir(parents=True, exist_ok=True)
    log_path = out_root / "run_log.md"
    if not log_path.exists():
        log_path.write_text("| date | items | topics | enriched | duration_s |\n"
                             "| --- | --- | --- | --- | --- |\n")
    with log_path.open("a") as f:
        f.write(f"| {run_date} | {num_items} | {num_topics} | {enriched} | {duration_s:.2f} |\n")


if __name__ == "__main__":
    sys.exit(main())
