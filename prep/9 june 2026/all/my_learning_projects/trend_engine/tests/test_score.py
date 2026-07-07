from trend_engine import score, store
from tests.test_store import _item

def test_zscore_spike():
    assert score.zscore(8400, [210, 180, 240, 195, 220, 205]) > 100

def test_zscore_zero_stddev_and_cold_start():
    assert score.zscore(100, [50, 50, 50]) > 0          # eps guard, no ZeroDivisionError
    assert score.zscore(100, []) == 1.0                 # cold start: neutral 1.0

def test_decay_monotonic():
    assert score.decay(1) > score.decay(10) > score.decay(100)

def test_corroboration():
    assert [score.corroboration(n) for n in (1, 2, 3, 5)] == [1.0, 1.5, 2.0, 2.0]

def test_niche_weight_stacks():
    assert score.niche_weight("Random cooking video") == 1.0
    assert score.niche_weight("New AI model") == 1.5
    assert abs(score.niche_weight("AI boom in India") - 1.95) < 1e-9
    assert score.niche_weight("How to maintain your car") == 1.0
    assert score.niche_weight("Explain again please") == 1.0
    assert score.niche_weight("AI beats humans") == 1.5

def test_is_excluded():
    assert score.is_excluded("Cricket star died today") is True
    assert score.is_excluded("New AI model released") is False

def test_rank_topics_drops_excluded_topics(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(topic="cricket world cup final", eng=9000),
                              _item(topic="ai model launch", eng=100)])
    ranked = score.rank_topics(conn)
    keys = [t["topic_key"] for t in ranked]
    assert "cricket world cup final" not in keys
    assert "ai model launch" in keys

def test_rank_topics_orders_and_limits(tmp_path):
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(topic="ai spike", eng=5000),
                              _item(topic="flat story", eng=100)])
    ranked = score.rank_topics(conn, limit=1)
    assert len(ranked) == 1 and ranked[0]["topic_key"] == "ai spike"
    assert ranked[0]["score"] > 0

def test_rank_topics_cold_start_percentile_orders_by_engagement(tmp_path):
    """Day-1 (empty DB): topics with no history must still rank by today's engagement."""
    conn = store.connect(tmp_path / "t.db")
    store.insert_items(conn, [_item(topic="hot topic", eng=500),
                              _item(topic="cold topic", eng=10)])
    ranked = score.rank_topics(conn)
    keys = [t["topic_key"] for t in ranked]
    assert keys.index("hot topic") < keys.index("cold topic")
    assert ranked[0]["topic_key"] == "hot topic"
    # the two topics must not have identical scores (would happen under old flat-1.0 z_norm)
    scores = {t["topic_key"]: t["score"] for t in ranked}
    assert scores["hot topic"] != scores["cold topic"]
