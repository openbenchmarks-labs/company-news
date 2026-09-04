from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    output: list[Hit] = []
    for row in (payload or {}).get("results") or []:
        highlights = row.get("highlights") or []
        item = hit(row.get("url"), row.get("title"), " ".join(highlights) or row.get("text"))
        if item:
            output.append(item)
    return output


def _adapter(search_type: str) -> WebAdapter:
    def build(case: Case):
        return (
            "POST", "https://api.exa.ai/search",
            {"x-api-key": os.environ["EXA_API_KEY"], "Content-Type": "application/json"},
            {"query": case.question, "type": search_type, "numResults": 10, "contents": {"highlights": True}},
            None, 45,
        )
    return WebAdapter(f"exa_{search_type}", "https://docs.exa.ai/reference/search", ("EXA_API_KEY",), build, _parse)


ADAPTERS = [_adapter("instant"), _adapter("fast")]

