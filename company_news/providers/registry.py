from __future__ import annotations

from .base import ProviderAdapter
from .news_indexes.autobound import ADAPTERS as AUTOBOUND
from .news_indexes.datahyena import ADAPTERS as DATAHYENA
from .news_indexes.predictleads import ADAPTERS as PREDICTLEADS
from .news_indexes.seltz import ADAPTERS as SELTZ
from .web_search.brave import ADAPTERS as BRAVE
from .web_search.exa import ADAPTERS as EXA
from .web_search.firecrawl import ADAPTERS as FIRECRAWL
from .web_search.linkup import ADAPTERS as LINKUP
from .web_search.parallel import ADAPTERS as PARALLEL
from .web_search.perplexity import ADAPTERS as PERPLEXITY
from .web_search.serp import ADAPTERS as SERP
from .web_search.tavily import ADAPTERS as TAVILY
from .web_search.tinyfish import ADAPTERS as TINYFISH
from .web_search.you import ADAPTERS as YOU

DEFAULT_ENDPOINTS = (
    "parallel_turbo", "parallel_fast", "parallel_basic", "exa_instant", "exa_fast",
    "brave", "brave_llm", "you", "you_highlights", "perplexity_low", "tinyfish",
    "firecrawl", "predictleads_category", "datahyena", "autobound", "seltz_news",
    "tavily_ultrafast", "serp", "linkup_fast", "linkup_standard",
)


def all_adapters() -> dict[str, ProviderAdapter]:
    adapters = [*PARALLEL, *EXA, *BRAVE, *YOU, *PERPLEXITY, *TINYFISH, *FIRECRAWL,
                *PREDICTLEADS, *DATAHYENA, *AUTOBOUND, *SELTZ, *TAVILY, *SERP, *LINKUP]
    result = {adapter.name: adapter for adapter in adapters}
    if len(result) != len(adapters):
        raise RuntimeError("duplicate provider endpoint name")
    return result


def selected_adapters(names: list[str] | tuple[str, ...] | None = None) -> list[ProviderAdapter]:
    registry = all_adapters()
    selected = list(names or DEFAULT_ENDPOINTS)
    unknown = sorted(set(selected) - set(registry))
    if unknown:
        raise ValueError(f"unknown endpoints: {', '.join(unknown)}")
    return [registry[name] for name in selected]

