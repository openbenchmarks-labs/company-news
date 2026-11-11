from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit

from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    output: list[Hit] = []
    for row in payload.get("results") or []:
        highlights = row.get("highlights") or {}
        parts = highlights.get("highlights") or []
        snippet = "\n".join(part for part in parts if isinstance(part, str)) if highlights.get("code") == "SUCCESS" else ""
        item = hit(row.get("url"), row.get("title"), snippet.strip() or row.get("description") or "")
        if item:
            output.append(item)
    return output


def _build(case: Case):
    return (
        "POST", "https://api.context.dev/v1/web/search",
        {"Authorization": f"Bearer {os.environ['CONTEXT_API_KEY']}", "Content-Type": "application/json"},
        {"query": case.question, "numResults": 10, "highlightsOptions": {"enabled": True}},
        None, 90,
    )


ADAPTERS = [WebAdapter(
    "context", "https://docs.context.dev/api-reference/web-scraping/search",
    ("CONTEXT_API_KEY",), _build, _parse,
)]
