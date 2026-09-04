from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    return [item for row in (payload or {}).get("results") or [] if (item := hit(row.get("url") or row.get("link"), row.get("title"), row.get("description") or row.get("snippet")))]


def _build(case: Case):
    return "GET", "https://google-search74.p.rapidapi.com/", {"x-rapidapi-key": os.environ["RAPIDAPI_KEY"], "x-rapidapi-host": "google-search74.p.rapidapi.com"}, None, {"query": case.question, "limit": 10}, 45


ADAPTERS = [WebAdapter("serp", "https://rapidapi.com/letscrape-6bRBa3QguO5/api/google-search74", ("RAPIDAPI_KEY",), _build, _parse)]

