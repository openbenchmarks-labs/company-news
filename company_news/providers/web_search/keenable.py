from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    rows = payload.get("results") if isinstance(payload, dict) else None
    output: list[Hit] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        item = hit(row.get("url"), row.get("title"), row.get("snippet") or row.get("description"))
        if item:
            output.append(item)
    return output


def _adapter(mode: str) -> WebAdapter:
    def build(case: Case):
        return (
            "POST", "https://api.keenable.ai/v1/search",
            {"X-API-Key": os.environ["KEENABLE_API_KEY"], "Content-Type": "application/json"},
            {"query": case.question, "mode": mode, "max_results": 10},
            None, 45,
        )
    return WebAdapter(f"keenable_{mode}", "https://docs.keenable.ai/api-reference/search",
                      ("KEENABLE_API_KEY",), build, _parse)


ADAPTERS = [_adapter("pro"), _adapter("realtime")]
