from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    rows = payload.get("results") if isinstance(payload, dict) else None
    output: list[Hit] = []
    seen: set[str] = set()
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("url"), str):
            continue
        url = row["url"].strip()
        if not url or url in seen:
            continue
        item = hit(url, row.get("title"), row.get("description"))
        if item:
            seen.add(url)
            output.append(item)
        if len(output) >= 10:
            break
    return output


def _adapter(depth: str, focus: str = "general") -> WebAdapter:
    name = f"nimble_{depth}" + ("_news" if focus == "news" else "")
    def build(case: Case):
        body = {"query": case.question, "search_depth": depth,
                "full_content": False, "focus": focus, "max_results": 10}
        return "POST", "https://sdk.nimbleway.com/v2/search", {"Authorization": f"Bearer {os.environ['NIMBLE_API_KEY']}", "Content-Type": "application/json"}, body, None, 60
    return WebAdapter(name, "https://docs.nimbleway.com/api-reference/search/search", ("NIMBLE_API_KEY",), build, _parse)


ADAPTERS = [_adapter("lite"), _adapter("lite", "news"), _adapter("standard")]
