from __future__ import annotations

import os
from typing import Any

from company_news.http import request_json
from company_news.models import Case, Hit, SearchResult
from company_news.providers.base import ProviderAdapter, dedupe, hit
from .common import skipped

RECIPE_SUBTYPES = {
    "receives_financing": ("receives_financing", "funding", "invests_into"),
    "financing_lead": ("receives_financing", "funding", "invests_into"),
    "acquires": ("acquires", "sells_assets_to", "merges_with"),
    "hires": ("hires", "promotes"),
    "launches": ("launches", "is_developing"),
    "decreases_headcount_by": ("decreases_headcount_by",),
    "expands_offices_to": ("expands_offices_to", "expands_offices_in", "expands_facilities", "opens_new_location"),
    "signs_new_client": ("signs_new_client",),
}


def _parse(payload: Any) -> list[Hit]:
    output: list[Hit] = []
    for signal in (payload or {}).get("signals") or []:
        detail = signal.get("data") if isinstance(signal.get("data"), dict) else {}
        event_id = signal.get("signal_id") or ""
        url = detail.get("url") or (f"https://signals.autobound.ai/v1/signals/{event_id}" if event_id else "")
        title = detail.get("title") or detail.get("signal_name") or signal.get("signal_name")
        snippet = " ".join(str(value) for value in (
            signal.get("signal_subtype"), detail.get("published_at") or signal.get("detected_at"),
            detail.get("summary"), detail.get("article_sentence"), detail.get("body"),
        ) if value)
        item = hit(url, title, snippet)
        if item:
            output.append(item)
    return output


class AutoboundAdapter(ProviderAdapter):
    name = "autobound"
    surface = "news-index"
    docs_url = "https://docs.autobound.ai"
    required_env = ("AUTOBOUND_API_KEY",)

    def search(self, case: Case) -> SearchResult:
        self.validate_credentials()
        subtypes = RECIPE_SUBTYPES.get(case.pattern)
        if not case.company_domain or not subtypes:
            return skipped(self.name, case, "company_domain or supported pattern unavailable")
        audit = request_json(
            "POST", "https://signals.autobound.ai/v1/companies/enrich",
            headers={"X-API-KEY": os.environ["AUTOBOUND_API_KEY"], "Content-Type": "application/json"},
            body={"domain": case.company_domain, "signal_types": ["news"],
                  "signal_subtypes": list(subtypes), "limit": 10}, timeout=45,
        )
        if audit.status_code == 404:
            audit.ok, audit.error = True, ""
        return SearchResult(endpoint=self.name, surface=self.surface,
                            hits=dedupe(_parse(audit.response)) if audit.ok else [], audit=audit)


ADAPTERS = [AutoboundAdapter()]

