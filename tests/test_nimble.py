from unittest.mock import patch
import pytest
from company_news.models import Case
from company_news.providers import all_adapters, DEFAULT_ENDPOINTS
from company_news.pricing import USD_PER_REQUEST

@pytest.mark.parametrize("name,depth,focus,price", [
    ("nimble_lite", "lite", "general", .0011),
    ("nimble_lite_news", "lite", "news", .0011),
    ("nimble_standard", "standard", "general", .005),
])
def test_search_contract_and_evidence(name, depth, focus, price):
    adapter = all_adapters()[name]
    with patch.dict("os.environ", {"NIMBLE_API_KEY": "test"}):
        method, url, headers, body, params, timeout = adapter.build(Case(id="q", question="Original question?"))
    assert body == {"query": "Original question?", "search_depth": depth, "focus": focus, "full_content": False, "max_results": 10}
    assert (method, url, params, timeout) == ("POST", "https://sdk.nimbleway.com/v2/search", None, 60)
    assert headers["Authorization"] == "Bearer test"
    rows = [None, {}, {"url": ""}, {"url": "https://example.com", "description": "snippet", "content": "FULL PAGE"}, {"url": "https://example.com"}]
    rows += [{"url": f"https://example.com/{i}"} for i in range(20)]
    hits = adapter.parse({"results": rows})
    assert len(hits) == 10
    assert hits[0].snippet == "snippet"
    assert hits[1].snippet == ""
    assert len({h.url for h in hits}) == 10
    assert adapter.parse(None) == []
    assert name in DEFAULT_ENDPOINTS
    assert USD_PER_REQUEST[name] == price
