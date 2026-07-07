import json
from unittest.mock import patch
from trend_engine import enrich

CANDS = [{"topic_key": "gpt 6 leaked benchmarks", "title": "GPT-6 leaked benchmarks", "score": 9.1,
          "sources": ["hackernews", "reddit"], "urls": ["u1"]},
         {"topic_key": "gpt 6 is insane", "title": "GPT-6 is INSANE", "score": 4.0,
          "sources": ["youtube"], "urls": ["u2"]}]

GOOD = json.dumps({"topics": [{"canonical_key": "gpt 6 leaked benchmarks",
        "merged_keys": ["gpt 6 is insane"], "explanation": "Leaked GPT-6 benchmarks are spreading.",
        "category": "AI", "platform_fit": "short-video", "stage": "rising"}]})

def test_enrich_merges_and_annotates():
    with patch.object(enrich, "_call_llm", return_value=GOOD):
        out, ok = enrich.enrich(CANDS)
    assert ok and len(out) == 1
    assert out[0]["score"] == 13.1 and out[0]["category"] == "AI"

def test_degraded_mode_after_retry():
    with patch.object(enrich, "_call_llm", side_effect=Exception("api down")) as m:
        out, ok = enrich.enrich(CANDS)
    assert not ok and len(out) == 2 and out[0]["category"] == "unclassified"
    assert m.call_count == 2  # one retry

def test_parse_rejects_bad_json():
    import pytest
    with pytest.raises(ValueError):
        enrich._parse("not json at all", CANDS)

DUP_CANDS = [{"topic_key": "a", "title": "A", "score": 5, "sources": ["x"], "urls": ["u1"]},
             {"topic_key": "b", "title": "B", "score": 3, "sources": ["y"], "urls": ["u2"]}]

def test_duplicate_merged_keys_sum_once():
    resp = json.dumps({"topics": [{"canonical_key": "a", "merged_keys": ["b", "b"],
            "explanation": "dup merge", "category": "AI", "platform_fit": "short-video",
            "stage": "rising"}]})
    out = enrich._parse(resp, DUP_CANDS)
    assert len(out) == 1
    assert out[0]["score"] == 8

def test_duplicate_canonical_key_across_clusters_yields_one_row():
    resp = json.dumps({"topics": [
        {"canonical_key": "a", "merged_keys": [], "explanation": "first claim",
         "category": "AI", "platform_fit": "short-video", "stage": "rising"},
        {"canonical_key": "a", "merged_keys": ["b"], "explanation": "second claim, reuses a",
         "category": "AI", "platform_fit": "short-video", "stage": "rising"},
    ]})
    out = enrich._parse(resp, DUP_CANDS)
    a_rows = [t for t in out if t["topic_key"] == "a"]
    assert len(a_rows) == 1
    assert a_rows[0]["score"] == 5
    # "b" was never consumed since the cluster claiming it was skipped, so it passes through.
    b_rows = [t for t in out if t["topic_key"] == "b"]
    assert len(b_rows) == 1
    assert b_rows[0]["category"] == "unclassified"

def test_invalid_enum_values_fall_back():
    resp = json.dumps({"topics": [{"canonical_key": "a", "merged_keys": [],
            "explanation": "x" * 400, "category": "AI-ish junk",
            "platform_fit": "carrier-pigeon", "stage": "explosive"}]})
    out = enrich._parse(resp, DUP_CANDS)
    row = [t for t in out if t["topic_key"] == "a"][0]
    assert row["category"] == "other"
    assert row["platform_fit"] == "short-video"
    assert row["stage"] == "rising"
    assert len(row["explanation"]) == 300

def test_non_string_merged_key_element_is_skipped():
    resp = json.dumps({"topics": [{"canonical_key": "a", "merged_keys": [{"bad": "dict"}, "b"],
            "explanation": "mixed types", "category": "AI", "platform_fit": "short-video",
            "stage": "rising"}]})
    out = enrich._parse(resp, DUP_CANDS)
    row = [t for t in out if t["topic_key"] == "a"][0]
    assert row["score"] == 8
