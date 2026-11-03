from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit

from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    data = payload.get("data") if isinstance(payload, dict) else None
    rows = data.get("results") if isinstance(data, dict) else None
    return [item for row in rows or [] if (item := hit(row.get("url"), row.get("title"), row.get("snippet")))]


def _build(case: Case):
    return (
        "POST", "https://api.hydrafetch.com/v1/web/search",
        {"X-API-Key": os.environ["HYDRAFETCH_API_KEY"], "Content-Type": "application/json"},
        {"query": case.question, "limit": 10, "scrapeResults": False}, None, 60,
    )


ADAPTERS = [WebAdapter(
    "hydrafetch", "https://docs.hydrafetch.com/api-reference/search/search-the-web",
    ("HYDRAFETCH_API_KEY",), _build, _parse,
)]
