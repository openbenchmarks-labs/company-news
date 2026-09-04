from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    results = (payload or {}).get("results") if isinstance(payload, dict) else payload
    rows = list((results or {}).get("web") or []) + list((results or {}).get("news") or []) if isinstance(results, dict) else results or []
    output: list[Hit] = []
    for row in rows:
        contents = row.get("contents") if isinstance(row.get("contents"), dict) else {}
        parts = contents.get("highlights") or row.get("highlights") or row.get("snippets") or []
        text = "\n".join(str(part.get("text") or part) if isinstance(part, dict) else str(part) for part in parts)
        item = hit(row.get("url"), row.get("title"), text or row.get("description") or row.get("snippet"))
        if item:
            output.append(item)
    return output


def _adapter(highlights: bool) -> WebAdapter:
    name = "you_highlights" if highlights else "you"
    def build(case: Case):
        body: dict[str, Any] = {"query": case.question, "count": 10}
        if highlights:
            body["extraction"] = {"extraction_mode": "highlights"}
        return "POST", "https://ydc-index.io/v1/search", {"X-API-Key": os.environ["YDC_API_KEY"], "Content-Type": "application/json"}, body, None, 45 if highlights else 30
    return WebAdapter(name, "https://documentation.you.com/api-reference/search", ("YDC_API_KEY",), build, _parse)


ADAPTERS = [_adapter(False), _adapter(True)]

