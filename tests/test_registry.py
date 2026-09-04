from company_news.providers import DEFAULT_ENDPOINTS, all_adapters


def test_default_roster_is_twenty_unique_endpoints():
    adapters = all_adapters()
    assert len(DEFAULT_ENDPOINTS) == 20
    assert len(set(DEFAULT_ENDPOINTS)) == 20
    assert set(DEFAULT_ENDPOINTS) <= set(adapters)
    assert {adapters[name].surface for name in DEFAULT_ENDPOINTS} == {"web-search", "news-index"}

