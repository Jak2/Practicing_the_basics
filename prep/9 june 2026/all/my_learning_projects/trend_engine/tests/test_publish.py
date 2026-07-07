import json
from trend_engine import publish, store

TOPICS = [{"topic_key": "gpt 6", "title": "GPT-6 leak", "score": 13.1, "urls": ["u1"],
           "sources": ["hackernews"], "explanation": "Benchmarks leaked.", "category": "AI",
           "platform_fit": "short-video", "stage": "rising"}]

def test_publish_writes_files(tmp_path):
    day = publish.publish(TOPICS, enriched=True, run_date="2026-07-02", out_root=tmp_path)
    assert (day / "top100.html").exists() and (day / "briefs" / "youtube.html").exists()
    data = json.loads((day / "top100.json").read_text())
    assert data["topics"][0]["title"] == "GPT-6 leak" and data["enriched"] is True

def test_degraded_banner(tmp_path):
    day = publish.publish(TOPICS, enriched=False, run_date="2026-07-02", out_root=tmp_path)
    assert "degraded" in (day / "top100.html").read_text().lower()

def test_degraded_banner_on_briefs(tmp_path):
    topics = [{"topic_key": "gpt 6", "title": "GPT-6 leak", "score": 13.1, "urls": ["u1"],
               "sources": ["hackernews"], "explanation": "Benchmarks leaked.", "category": "AI",
               "platform_fit": "short-video", "stage": "rising"}]
    day = publish.publish(topics, enriched=False, run_date="2026-07-02", out_root=tmp_path)
    brief_html = (day / "briefs" / "youtube.html").read_text()
    assert "degraded" in brief_html.lower()

def test_score_rendered_rounded(tmp_path):
    topics = [{"topic_key": "gpt 6", "title": "GPT-6 leak", "score": 13.146789, "urls": ["u1"],
               "sources": ["hackernews"], "explanation": "Benchmarks leaked.", "category": "AI",
               "platform_fit": "short-video", "stage": "rising"}]
    day = publish.publish(topics, enriched=True, run_date="2026-07-02", out_root=tmp_path)
    html_content = (day / "top100.html").read_text()
    assert "(13.15)" in html_content

def test_save_to_db(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    publish.save_to_db(conn, TOPICS, "2026-07-02")
    assert conn.execute("SELECT COUNT(*) FROM daily_top100").fetchone()[0] == 1

def test_safe_href_javascript(tmp_path):
    """Test that javascript: URIs are rendered as href='#'."""
    topics = [{"topic_key": "test", "title": "Test", "score": 1.0,
               "urls": ["javascript:alert(1)"], "explanation": "Test",
               "category": "Test", "platform_fit": "short-video", "stage": "rising"}]
    day = publish.publish(topics, enriched=True, run_date="2026-07-02", out_root=tmp_path)
    html_content = (day / "top100.html").read_text()
    # Verify href="#" is present (safe version)
    assert 'href="#"' in html_content
    # Verify the raw javascript: string does not appear in any href attribute
    assert "javascript:" not in html_content or 'href="javascript:' not in html_content

def test_save_to_db_idempotent(tmp_path):
    """Test that calling save_to_db twice with the same run_date leaves exactly len(topics) rows."""
    conn = store.connect(tmp_path / "t.db")
    publish.save_to_db(conn, TOPICS, "2026-07-02")
    count_after_first = conn.execute("SELECT COUNT(*) FROM daily_top100").fetchone()[0]
    assert count_after_first == len(TOPICS)

    # Call save_to_db again with the same run_date
    publish.save_to_db(conn, TOPICS, "2026-07-02")
    count_after_second = conn.execute("SELECT COUNT(*) FROM daily_top100").fetchone()[0]
    assert count_after_second == len(TOPICS)  # Should still be exactly 1, not 2
