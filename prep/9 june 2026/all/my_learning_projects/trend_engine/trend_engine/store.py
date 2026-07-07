import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_items (
  id INTEGER PRIMARY KEY, topic_key TEXT NOT NULL, source TEXT NOT NULL,
  title TEXT, url TEXT, engagement REAL, engagement_type TEXT,
  region TEXT, fetched_at TEXT NOT NULL, content_created_at TEXT,
  fetched_date TEXT GENERATED ALWAYS AS (substr(fetched_at, 1, 10)) STORED
);
CREATE INDEX IF NOT EXISTS idx_raw_topic_date ON raw_items(topic_key, fetched_date);
CREATE TABLE IF NOT EXISTS daily_top100 (
  run_date TEXT, rank INTEGER, topic_key TEXT, title TEXT, score REAL,
  explanation TEXT, category TEXT, platform_fit TEXT, stage TEXT, urls TEXT,
  PRIMARY KEY (run_date, rank)
);
"""

def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    _migrate_content_created_at(conn)
    return conn

def _migrate_content_created_at(conn):
    """Add content_created_at to a raw_items table created before this column existed."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(raw_items)")}
    if "content_created_at" not in cols:
        conn.execute("ALTER TABLE raw_items ADD COLUMN content_created_at TEXT")
        conn.commit()

def insert_items(conn, items):
    conn.executemany(
        "INSERT INTO raw_items (topic_key, source, title, url, engagement, engagement_type,"
        " region, fetched_at, content_created_at)"
        " VALUES (:topic_key, :source, :title, :url, :engagement, :engagement_type, :region,"
        " :fetched_at, :content_created_at)",
        [{**item, "content_created_at": item.get("content_created_at")} for item in items])
    conn.commit()

def topic_history(conn, topic_key, days=7):
    rows = conn.execute(
        "SELECT fetched_date, SUM(engagement) FROM raw_items"
        " WHERE topic_key = ? AND fetched_date < date('now')"
        "   AND fetched_date >= date('now', ?)"
        " GROUP BY fetched_date ORDER BY fetched_date",
        (topic_key, f"-{days} days")).fetchall()
    return [float(r[1]) for r in rows]

def todays_topics(conn):
    rows = conn.execute(
        "SELECT topic_key, MAX(title), SUM(engagement),"
        "       GROUP_CONCAT(DISTINCT source), GROUP_CONCAT(DISTINCT region),"
        "       (julianday('now') - julianday(MIN(COALESCE(content_created_at, fetched_at)))) * 24"
        " FROM raw_items WHERE fetched_date = date('now') GROUP BY topic_key").fetchall()

    url_rows = conn.execute(
        "SELECT topic_key, url FROM raw_items"
        " WHERE fetched_date = date('now') AND url IS NOT NULL").fetchall()
    urls_by_topic = {}
    for topic_key, url in url_rows:
        seen = urls_by_topic.setdefault(topic_key, [])
        if url not in seen:
            seen.append(url)

    return [{"topic_key": r[0], "title": r[1], "engagement": float(r[2]),
             "sources": r[3].split(","), "regions": r[4].split(","),
             "first_seen_hours": float(r[5]), "urls": urls_by_topic.get(r[0], [])} for r in rows]
