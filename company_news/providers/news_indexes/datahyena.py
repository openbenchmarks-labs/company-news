from __future__ import annotations

import os
from typing import Any

from company_news.http import request_json
from company_news.models import Case, Hit, SearchResult
from company_news.providers.base import ProviderAdapter, dedupe, hit
from .common import skipped

RECIPE_INCLUDE = {
    "receives_financing": "funding", "financing_lead": "funding",
    "acquires": "acquisitions", "hires": "exec_moves",
}


def _source_url(record: dict[str, Any]) -> str:
    for key in ("sources", "sourceUrls", "articles", "urls", "citations"):
        values = record.get(key) or []
        for value in values if isinstance(values, list) else [values]:
            if isinstance(value, str) and value.startswith("http"):
                return value
            if isinstance(value, dict):
                for field in ("url", "sourceUrl", "href", "link"):
                    if str(value.get(field) or "").startswith("http"):
                        return str(value[field])
    return ""


def _parse(payload: Any) -> list[Hit]:
    events = (((payload or {}).get("data") or {}).get("events") or [])
    output: list[Hit] = []
    for outer in events:
        record = next((outer[key] for key in ("funding", "acquisition", "execMove", "exec_move") if isinstance(outer.get(key), dict)), outer)
        company = ((record.get("company") or {}).get("name") if isinstance(record.get("company"), dict) else "")
        text = " ".join(str(value) for value in (
            company, record.get("round"), record.get("amountUsd"), record.get("dealAmountUsd"),
            (record.get("person") or {}).get("name") if isinstance(record.get("person"), dict) else "",
            record.get("role"), record.get("announcedAt") or record.get("effectiveDate"),
        ) if value)
        event_id = record.get("id") or outer.get("id")
        url = _source_url(record) or (f"https://datahyena.com/events/{event_id}" if event_id else "")
        item = hit(url, text, text)
        if item:
            output.append(item)
    return output


class DatahyenaAdapter(ProviderAdapter):
    name = "datahyena"
    surface = "news-index"
    docs_url = "https://docs.datahyena.com"
    required_env = ("DATAHYENA_API_KEY",)

    def search(self, case: Case) -> SearchResult:
        self.validate_credentials()
        include = RECIPE_INCLUDE.get(case.pattern)
        if not case.company_domain or not include:
            return skipped(self.name, case, "company_domain or supported pattern unavailable")
        audit = request_json(
            "GET", "https://api.datahyena.com/v1/companies/timeline",
            headers={"X-API-Key": os.environ["DATAHYENA_API_KEY"], "Accept": "application/json"},
            params={"domain": case.company_domain, "include": include}, timeout=45,
        )
        if audit.status_code == 404:
            audit.ok, audit.error = True, ""
        return SearchResult(endpoint=self.name, surface=self.surface,
                            hits=dedupe(_parse(audit.response)) if audit.ok else [], audit=audit)


ADAPTERS = [DatahyenaAdapter()]

