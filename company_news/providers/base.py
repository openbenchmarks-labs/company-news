from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Literal
from urllib.parse import urlparse

from company_news.models import Case, Hit, SearchResult


def require_env(*names: str) -> tuple[str, ...]:
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"missing credentials: {', '.join(missing)}")
    return tuple(os.environ[name] for name in names)


def hit(url: Any, title: Any = "", snippet: Any = "", **metadata: Any) -> Hit | None:
    clean_url = str(url or "").strip()
    if not clean_url:
        return None
    return Hit(
        url=clean_url,
        title=str(title or "").strip(),
        snippet=str(snippet or "").strip()[:8000],
        metadata=metadata,
    )


def dedupe(rows: list[Hit], limit: int = 10) -> list[Hit]:
    seen: set[str] = set()
    output: list[Hit] = []
    for row in rows:
        parsed = urlparse(row.url)
        key = f"{parsed.netloc.lower().removeprefix('www.')}{parsed.path.rstrip('/')}"
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(row)
        if len(output) == limit:
            break
    return output


class ProviderAdapter(ABC):
    name: str
    surface: Literal["web-search", "news-index"]
    docs_url: str
    required_env: tuple[str, ...]

    def validate_credentials(self) -> None:
        require_env(*self.required_env)

    @abstractmethod
    def search(self, case: Case) -> SearchResult:
        raise NotImplementedError

