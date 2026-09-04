from company_news.artifacts import write_json
from company_news.orchestration import build_snapshot
from company_news.verification import verify_run


def test_snapshot_manifest_round_trip(tmp_path):
    write_json(tmp_path / "run-plan.json", {
        "dataset": "/tmp/input.json", "dataset_sha256": "abc", "case_count": 1,
        "endpoints": ["exa_instant"], "case_concurrency": 1,
        "provider_calls_within_case": "parallel", "max_results": 10,
        "search_only": True, "started_at": "2026-09-04T00:00:00+00:00",
    })
    audit = {
        "method": "GET", "url": "https://example.com", "request": {"headers": {"X-Api-Key": "***REDACTED***"}},
        "response": {}, "ok": True, "status_code": 200, "error": "", "attempts": [],
        "latency_ms": 10, "started_at": "start", "ended_at": "end",
    }
    write_json(tmp_path / "audit/case/exa_instant.json", audit)
    write_json(tmp_path / "cells/case/exa_instant.json", {
        "case_id": "case", "question": "q", "endpoint": "exa_instant", "surface": "web-search",
        "ok": True, "latency_ms": 10, "ground_truth_url": "", "hits": [],
        "audit_path": "audit/case/exa_instant.json", "evaluation": None,
    })
    build_snapshot(tmp_path)
    assert verify_run(tmp_path)["cells"] == 1

