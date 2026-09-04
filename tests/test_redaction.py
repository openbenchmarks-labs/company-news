from company_news.http import redact_headers


def test_secret_headers_are_redacted():
    headers = redact_headers({"Authorization": "Bearer secret", "X-Api-Key": "secret", "Accept": "application/json"})
    assert headers["Authorization"] == "***REDACTED***"
    assert headers["X-Api-Key"] == "***REDACTED***"
    assert headers["Accept"] == "application/json"

