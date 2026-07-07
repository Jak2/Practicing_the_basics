import datetime as dt
from trend_engine import store

def _item(topic="gpt-6 leak", eng=100.0, source="hackernews", region="GLOBAL",
          fetched_at=None, content_created_at=None):
    return {"topic_key": topic, "source": source, "title": topic.title(), "url": "https://x.com/1",
            "engagement": eng, "engagement_type": "points", "region": region,
            "fetched_at": (fetched_at or dt.datetime.now(dt.timezone.utc)).isoformat(),
            "content_created_at": content_created_at}

def test_schema_created(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"raw_items", "daily_top100"} <= names

def test_connect_migrates_pre_existing_db_missing_content_created_at(tmp_path):
    db_path = tmp_path / "old.db"
    import sqlite3
    old_conn = sqlite3.connect(db_path)
    old_conn.executescript(
        "CREATE TABLE raw_items (id INTEGER PRIMARY KEY, topic_key TEXT NOT NULL,"
        " source TEXT NOT NULL, title TEXT, url TEXT, engagement REAL,"
        " engagement_type TEXT, region TEXT, fetched_at TEXT NOT NULL,"
        " fetched_date TEXT GENERATED ALWAYS AS (substr(fetched_at, 1, 10)) STORED);"
    )
    old_conn.commit()
    old_conn.close()

    conn = store.connect(db_path)  # must not raise
    cols = {row[1] for row in conn.execute("PRAGMA table_info(raw_items)")}
    assert "content_created_at" in cols

def test_insert_and_todays_topics(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(eng=50), _item(eng=70, source="reddit")])
    topics = store.todays_topics(conn)
    assert len(topics) == 1
    t = topics[0]
    assert t["topic_key"] == "gpt-6 leak"
    assert t["engagement"] == 120
    assert sorted(t["sources"]) == ["hackernews", "reddit"]

def test_todays_topics_urls_survive_commas(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    comma_url = "https://example.com/x?a=1,2"
    item1 = _item(eng=50)
    item1["url"] = comma_url
    item2 = _item(eng=70, source="reddit")
    item2["url"] = "https://y.com/2"
    store.insert_items(conn, [item1, item2])
    topics = store.todays_topics(conn)
    assert len(topics) == 1
    assert sorted(topics[0]["urls"]) == sorted([comma_url, "https://y.com/2"])

def test_todays_topics_uses_content_created_at_when_present(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    now = dt.datetime.now(dt.timezone.utc)
    old_content_time = now - dt.timedelta(hours=10)
    # fetched_at is "now" (fresh collection) but the actual post is 10h old —
    # first_seen_hours must reflect the post's real age, not collection time.
    item = _item(content_created_at=old_content_time.isoformat())
    store.insert_items(conn, [item])
    topics = store.todays_topics(conn)
    assert len(topics) == 1
    assert topics[0]["first_seen_hours"] >= 9.9

def test_todays_topics_falls_back_to_fetched_at_when_content_created_at_missing(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(content_created_at=None)])
    topics = store.todays_topics(conn)
    assert topics[0]["first_seen_hours"] < 0.1  # fetched just now, no content timestamp

def test_topic_history_excludes_today(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    now = dt.datetime.now(dt.timezone.utc)
    for d, eng in [(3, 10), (2, 20), (1, 30), (0, 999)]:
        store.insert_items(conn, [_item(eng=eng, fetched_at=now - dt.timedelta(days=d))])
    assert store.topic_history(conn, "gpt-6 leak", days=7) == [10.0, 20.0, 30.0]
