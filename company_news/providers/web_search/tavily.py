from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    return [item for row in (payload or {}).get("results") or [] if (item := hit(row.get("url"), row.get("title"), row.get("content")))]


def _build(case: Case):
    return "POST", "https://api.tavily.com/search", {"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}", "Content-Type": "application/json"}, {"query": case.question, "search_depth": "ultra-fast", "max_results": 10}, None, 45


ADAPTERS = [WebAdapter("tavily_ultrafast", "https://docs.tavily.com/documentation/api-reference/endpoint/search", ("TAVILY_API_KEY",), _build, _parse)]

