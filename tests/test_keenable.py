from unittest.mock import MagicMock, patch

import pytest

from company_news.http import redact_headers
from company_news.metrics import aggregate
from company_news.models import Case
from company_news.pricing import USD_PER_REQUEST
from company_news.providers import DEFAULT_ENDPOINTS, all_adapters


def test_keenable_request_contract():
    adapter = all_adapters()["keenable"]
    with patch.dict("os.environ", {"KEENABLE_API_KEY": "test-key"}):
        method, url, headers, body, params, timeout = adapter.build(Case(id="q", question="Unchanged question?"))
    assert (method, url, params, timeout) == ("POST", "https://api.keenable.ai/v1/search", None, 45)
    assert body == {"query": "Unchanged question?", "mode": "pro", "max_results": 10}
    assert headers["X-API-Key"] == "test-key"
    assert adapter.required_env == ("KEENABLE_API_KEY",)
    assert adapter.surface == "web-search"


def test_keenable_parser_prefers_snippet_and_skips_bad_rows():
    adapter = all_adapters()["keenable"]
    rows = [
        None, {}, {"url": "", "snippet": "no url"}, {"title": "missing url", "snippet": "x"},
        {"url": "https://example.com/a", "title": "A", "description": "", "snippet": "Long snippet",
         "published_at": 1767225600},
        {"url": "https://example.com/b", "title": "B", "description": "Desc only", "snippet": ""},
        {"url": "https://www.example.com/a/", "title": "A dup", "snippet": "duplicate"},
    ]
    hits = adapter.parse({"query": "q", "mode": "pro", "results": rows})
    assert [h.url for h in hits] == ["https://example.com/a", "https://example.com/b", "https://www.example.com/a/"]
    assert hits[0].snippet == "Long snippet"
    assert hits[1].snippet == "Desc only"
    assert adapter.parse(None) == []
    assert adapter.parse({}) == []
    assert adapter.parse({"results": None}) == []


def test_keenable_search_dedupes_and_redacts_key():
    adapter = all_adapters()["keenable"]
    response = MagicMock(status_code=200, ok=True)
    response.json.return_value = {"results": [
        {"url": "https://example.com/a", "title": "A", "snippet": "one"},
        {"url": "https://www.example.com/a/", "title": "A dup", "snippet": "two"},
        *[{"url": f"https://example.com/{i}", "snippet": "s"} for i in range(15)],
    ], "usage": {"sku": "search", "amount": 1, "credits": 1, "paid": True}}
    with patch.dict("os.environ", {"KEENABLE_API_KEY": "secret-key"}), \
            patch("company_news.http.requests.request", return_value=response) as request:
        result = adapter.search(Case(id="q", question="Q?"))
    assert request.call_args.args == ("POST", "https://api.keenable.ai/v1/search")
    assert request.call_args.kwargs["json"]["mode"] == "pro"
    assert len(result.hits) == 10
    assert [h.url for h in result.hits].count("https://www.example.com/a/") == 0
    assert result.audit.request["headers"]["X-API-Key"] == "***REDACTED***"
    assert "secret-key" not in result.audit.model_dump_json()


def test_keenable_failed_search_returns_no_hits():
    adapter = all_adapters()["keenable"]
    response = MagicMock(status_code=401, ok=False)
    response.json.return_value = {"detail": "unauthorized"}
    with patch.dict("os.environ", {"KEENABLE_API_KEY": "k"}), \
            patch("company_news.http.requests.request", return_value=response):
        result = adapter.search(Case(id="q", question="Q?"))
    assert not result.audit.ok
    assert result.hits == []


def test_x_api_key_header_redacted_case_insensitive():
    headers = redact_headers({"X-API-Key": "a", "x-api-key": "b", "X-Api-Key": "c"})
    assert set(headers.values()) == {"***REDACTED***"}


def test_keenable_roster_and_list_price():
    name = "keenable"
    # The repo prices per endpoint at list price (metrics.aggregate); usage.credits is not per-cell.
    assert name in DEFAULT_ENDPOINTS
    assert USD_PER_REQUEST[name] == 0.004
    row = aggregate([{"endpoint": name, "surface": "web-search", "ok": True, "hits": [],
                      "evaluation": {"accuracy": {"correct": True}}}])[0]
    assert row["list_price_per_query_usd"] == 0.004
    assert row["cost_per_1000_correct_usd"] == 4.0


def test_keenable_is_a_single_pro_arm():
    names = [name for name in all_adapters() if name.startswith("keenable")]
    assert names == ["keenable"]
    assert [name for name in DEFAULT_ENDPOINTS if name.startswith("keenable")] == ["keenable"]
