from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _web_parse(payload: Any) -> list[Hit]:
    rows = ((payload or {}).get("web") or {}).get("results") or []
    return [item for row in rows if (item := hit(row.get("url"), row.get("title"), row.get("description") or row.get("snippet")))]


def _llm_parse(payload: Any) -> list[Hit]:
    rows = ((payload or {}).get("grounding") or {}).get("generic") or []
    output: list[Hit] = []
    for row in rows:
        snippets = row.get("snippets") or []
        text = "\n".join(str(value) for value in snippets) if isinstance(snippets, list) else str(snippets)
        item = hit(row.get("url"), row.get("title"), text)
        if item:
            output.append(item)
    return output


def _web_build(case: Case):
    return (
        "GET", "https://api.search.brave.com/res/v1/web/search",
        {"X-Subscription-Token": os.environ["BRAVE_SEARCH_API_KEY"], "Accept": "application/json"},
        None, {"q": case.question, "count": 10, "result_filter": "web"}, 45,
    )


def _llm_build(case: Case):
    return (
        "POST", "https://api.search.brave.com/res/v1/llm/context",
        {"X-Subscription-Token": os.environ["BRAVE_SEARCH_API_KEY"], "Content-Type": "application/json"},
        {"q": case.question, "count": 10, "maximum_number_of_urls": 10,
         "maximum_number_of_tokens": 8192, "enable_local": False}, None, 30,
    )


ADAPTERS = [
    WebAdapter("brave", "https://api-dashboard.search.brave.com/documentation/services/web-search", ("BRAVE_SEARCH_API_KEY",), _web_build, _web_parse),
    WebAdapter("brave_llm", "https://api-dashboard.search.brave.com/documentation/services/llm-context", ("BRAVE_SEARCH_API_KEY",), _llm_build, _llm_parse),
]

