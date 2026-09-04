from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, Hit
from company_news.providers.base import hit
from .common import WebAdapter


def _parse(payload: Any) -> list[Hit]:
    return [item for row in (payload or {}).get("results") or [] if (item := hit(row.get("url"), row.get("title"), row.get("snippet") or row.get("description")))]


def _build(case: Case):
    return "GET", "https://api.search.tinyfish.ai", {"X-API-Key": os.environ["TINYFISH_API_KEY"], "Accept": "application/json"}, None, {"query": case.question}, 30


ADAPTERS = [WebAdapter("tinyfish", "https://docs.tinyfish.ai", ("TINYFISH_API_KEY",), _build, _parse)]

