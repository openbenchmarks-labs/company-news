from company_news import http


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def perf_counter(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = ""

    def json(self):
        return {"results": []}


def test_latency_is_the_successful_attempt_not_retries_and_backoff(monkeypatch):
    clock = FakeClock()
    responses = iter([(0.2, 429), (0.3, 200)])

    def fake_request(*args, **kwargs):
        seconds, status = next(responses)
        clock.now += seconds
        return FakeResponse(status)

    monkeypatch.setattr(http, "time", clock)
    monkeypatch.setattr(http.requests, "request", fake_request)

    audit = http.request_json("GET", "https://search.example", headers={})

    assert audit.ok
    assert [attempt.latency_ms for attempt in audit.attempts] == [200, 300]
    assert audit.latency_ms == 300
