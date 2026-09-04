from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    output: list[Hit] = []
    for row in (payload or {}).get("results") or []:
        item = hit(row.get("url"), row.get("title"), "\n".join(row.get("excerpts") or []))
        if item:
            output.append(item)
    return output


def _adapter(mode: str) -> WebAdapter:
    def build(case: Case):
        return (
            "POST", "https://api.parallel.ai/v1/search",
            {"x-api-key": os.environ["PARALLEL_API_KEY"], "Content-Type": "application/json"},
            {"objective": case.question, "search_queries": [case.question], "mode": mode,
             "advanced_settings": {"max_results": 10}},
            None, 90 if mode == "basic" else 60,
        )
    return WebAdapter(f"parallel_{mode}", "https://docs.parallel.ai/api-reference/search", ("PARALLEL_API_KEY",), build, _parse)


ADAPTERS = [_adapter(mode) for mode in ("turbo", "fast", "basic")]

