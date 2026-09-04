from __future__ import annotations

from company_news.http import now
from company_news.models import Case, HttpAudit, SearchResult


def skipped(endpoint: str, case: Case, reason: str) -> SearchResult:
    stamp = now()
    return SearchResult(
        endpoint=endpoint,
        surface="news-index",
        hits=[],
        audit=HttpAudit(
            method="SKIP", url="", request={"case_id": case.id}, response={"skip_reason": reason},
            ok=True, error="", attempts=[], latency_ms=0, started_at=stamp, ended_at=stamp,
        ),
    )
