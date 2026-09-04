from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from company_news.http import request_json
from company_news.models import Case, Hit, SearchResult
from company_news.providers.base import ProviderAdapter, dedupe

RequestBuilder = Callable[[Case], tuple[str, str, dict[str, str], dict[str, Any] | None, dict[str, Any] | None, int]]
Parser = Callable[[Any], list[Hit]]


@dataclass
class WebAdapter(ProviderAdapter):
    name: str
    docs_url: str
    required_env: tuple[str, ...]
    build: RequestBuilder
    parse: Parser
    surface: str = "web-search"

    def search(self, case: Case) -> SearchResult:
        self.validate_credentials()
        method, url, headers, body, params, timeout = self.build(case)
        audit = request_json(method, url, headers=headers, body=body, params=params, timeout=timeout)
        hits = dedupe(self.parse(audit.response), 10) if audit.ok else []
        return SearchResult(endpoint=self.name, surface="web-search", hits=hits, audit=audit)

