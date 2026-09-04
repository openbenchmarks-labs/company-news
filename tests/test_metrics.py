from company_news.metrics import aggregate


def test_accuracy_keeps_failures_in_denominator_and_latency_drops_them():
    cells = [
        {"endpoint": "exa_instant", "surface": "web-search", "ok": True, "latency_ms": 100,
         "ground_truth_url": "https://example.com/a", "hits": [{"url": "https://example.com/a", "title": "", "snippet": "answer"}],
         "evaluation": {"accuracy": {"correct": True}, "answer_recall": {"ar1": True, "ar5": True, "ar10": True}}},
        {"endpoint": "exa_instant", "surface": "web-search", "ok": False, "latency_ms": 999,
         "ground_truth_url": "https://example.com/b", "hits": [], "evaluation": None},
    ]
    row = aggregate(cells)[0]
    assert row["accuracy_pct"] == 50.0
    assert row["mean_latency_ms"] == 100.0
    assert row["successful_requests"] == 1

