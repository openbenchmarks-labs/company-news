from unittest.mock import patch

import pytest

from company_news.models import Case
from company_news.pricing import USD_PER_REQUEST
from company_news.providers import DEFAULT_ENDPOINTS, all_adapters


@pytest.mark.parametrize("name,core", [("you_highlights", False), ("you_highlights_core", True)])
def test_you_request_and_highlights(name, core):
    adapter = all_adapters()[name]
    with patch.dict("os.environ", {"YDC_API_KEY": "test-key"}):
        method, url, headers, body, params, timeout = adapter.build(Case(id="one", question="Unchanged question?"))
    expected = {"query": "Unchanged question?", "count": 10, "extraction": {"extraction_mode": "highlights"}}
    if core:
        expected["knowledge"] = "core"
    assert (method, url, body, params, timeout) == ("POST", "https://ydc-index.io/v1/search", expected, None, 45)
    assert headers["X-API-Key"] == "test-key"
    hits = adapter.parse({"results": {"web": [{"url": "https://example.com", "snippets": ["fallback"],
                        "contents": {"highlights": ["Relevant evidence"]}}]}})
    assert hits[0].snippet == "Relevant evidence"
    assert name in DEFAULT_ENDPOINTS
    assert USD_PER_REQUEST[name] == 0.005
