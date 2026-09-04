from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    return [item for row in (payload or {}).get("results") or [] if row.get("type") != "image" if (item := hit(row.get("url"), row.get("name") or row.get("title"), row.get("content") or row.get("snippet")))]


def _adapter(depth: str) -> WebAdapter:
    def build(case: Case):
        return "POST", "https://api.linkup.so/v1/search", {"Authorization": f"Bearer {os.environ['LINKUP_API_KEY']}", "Content-Type": "application/json"}, {"q": case.question, "depth": depth, "outputType": "searchResults", "maxResults": 10}, None, 60 if depth == "standard" else 45
    return WebAdapter(f"linkup_{depth}", "https://docs.linkup.so/pages/documentation/api-reference/endpoint/post-search", ("LINKUP_API_KEY",), build, _parse)


ADAPTERS = [_adapter("fast"), _adapter("standard")]

