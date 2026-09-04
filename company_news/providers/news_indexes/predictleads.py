from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from company_news.evaluation.extraction import parse_openai
from company_news.http import request_json
from company_news.models import Case, Hit, SearchResult
from company_news.providers.base import ProviderAdapter, dedupe, hit
from .common import skipped

RECIPE_CATEGORIES = {
    "receives_financing": ("receives_financing", "invests_into", "has_valuation"),
    "financing_lead": ("receives_financing", "invests_into", "has_valuation"),
    "acquires": ("acquires", "sells_assets_to"),
    "hires": ("hires", "promotes"),
    "launches": ("launches", "is_developing"),
    "decreases_headcount_by": ("decreases_headcount_by",),
    "expands_offices_to": ("expands_offices_to", "expands_offices_in", "expands_facilities", "opens_new_location"),
    "signs_new_client": ("signs_new_client",),
    "partners_with": ("partners_with",),
    "integrates_with": ("integrates_with",),
    "promotes": ("promotes", "hires"),
    "sells_assets_to": ("sells_assets_to", "acquires"),
}

ALLOWED_CATEGORIES = (
    "acquires", "attends_event", "closes_offices_in", "decreases_headcount_by",
    "expands_facilities", "expands_offices_in", "expands_offices_to", "files_suit_against",
    "goes_public", "has_earnings", "has_issues_with", "has_revenue", "has_valuation",
    "hires", "identified_as_competitor_of", "increases_headcount_by", "integrates_with",
    "invests_into", "invests_into_assets", "is_developing", "launches", "leaves",
    "opens_new_location", "partners_with", "promotes", "receives_award",
    "receives_financing", "recognized_as", "retires_from", "sells_assets_to",
    "signs_new_client", "spins_off_company",
)


class CategoryPick(BaseModel):
    categories: list[str] = Field(default_factory=list)
    reason: str = ""


def _select_categories(case: Case) -> tuple[list[str], str, dict[str, int]]:
    verdict, tokens = parse_openai(
        "Pick every PredictLeads news_event category that could contain the answer. "
        "Use only the supplied closed list. Prefer recall and include inverse or sibling tags. "
        "Choose at most five categories.",
        {"question": case.question, "recipe_hint": case.pattern,
         "allowed_categories": list(ALLOWED_CATEGORIES)},
        CategoryPick,
    )
    allowed = set(ALLOWED_CATEGORIES)
    picked = [category for category in verdict.categories if category in allowed]
    combined = list(dict.fromkeys([*picked, *RECIPE_CATEGORIES.get(case.pattern, ())]))[:5]
    return combined, verdict.reason, tokens


def _parse(payload: Any) -> list[Hit]:
    included: dict[tuple[str, str], dict[str, Any]] = {}
    for row in (payload or {}).get("included") or []:
        if isinstance(row, dict) and row.get("id"):
            included[(str(row.get("type") or ""), str(row["id"]))] = row.get("attributes") or {}
    output: list[Hit] = []
    for event in (payload or {}).get("data") or []:
        attrs = event.get("attributes") or {}
        source = (((event.get("relationships") or {}).get("most_relevant_source") or {}).get("data") or {})
        article = included.get(("news_article", str(source.get("id") or "")), {})
        snippet = " ".join(str(value) for value in (
            attrs.get("category"), attrs.get("effective_date"), attrs.get("amount"),
            attrs.get("summary"), attrs.get("article_sentence") or article.get("body"),
        ) if value)
        item = hit(article.get("url"), article.get("title") or attrs.get("summary"), snippet,
                   category=attrs.get("category"))
        if item:
            output.append(item)
    return output


class PredictLeadsAdapter(ProviderAdapter):
    name = "predictleads_category"
    surface = "news-index"
    docs_url = "https://predictleads.com/docs/#company-news-events"
    required_env = ("PREDICT_LEADS_API_KEY", "PREDICT_LEADS_API_TOKEN")

    def search(self, case: Case) -> SearchResult:
        self.validate_credentials()
        if not case.company_domain:
            return skipped(self.name, case, "company_domain is required")
        categories, reason, tokens = _select_categories(case)
        if not categories:
            return skipped(self.name, case, f"unsupported pattern: {case.pattern}")
        params: list[tuple[str, Any]] = [("limit", 10), ("page", 1)]
        params.extend(("categories[]", category) for category in categories)
        audit = request_json(
            "GET", f"https://predictleads.com/api/v3/companies/{case.company_domain}/news_events",
            headers={"X-Api-Key": os.environ["PREDICT_LEADS_API_KEY"],
                     "X-Api-Token": os.environ["PREDICT_LEADS_API_TOKEN"]},
            params=params, timeout=45,
        )
        audit.request["category_selection"] = {
            "categories": categories,
            "reason": reason,
            "tokens": tokens,
            "model": os.getenv("EXTRACT_MODEL", "gpt-5.6-terra"),
            "reasoning": os.getenv("EXTRACT_REASONING_EFFORT", "medium"),
        }
        rows = dedupe(_parse(audit.response)) if audit.ok else []
        return SearchResult(endpoint=self.name, surface=self.surface, hits=rows, audit=audit)


ADAPTERS = [PredictLeadsAdapter()]
