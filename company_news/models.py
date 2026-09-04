from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class GoldCell(BaseModel):
    label: str = "answer"
    value: str


class Case(BaseModel):
    id: str
    question: str
    company_domain: str = ""
    pattern: str = ""
    expected_answer: str = ""
    ground_truth_url: str = ""
    cells: list[GoldCell] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_record(cls, row: dict[str, Any]) -> "Case":
        gold = row.get("gold") if isinstance(row.get("gold"), dict) else {}
        known = {
            "id", "question", "company_domain", "pattern", "recipe",
            "expected_answer", "ground_truth", "ground_truth_url", "cells", "gold",
        }
        return cls(
            id=str(row["id"]),
            question=str(row["question"]),
            company_domain=str(row.get("company_domain") or gold.get("domain") or ""),
            pattern=str(row.get("pattern") or row.get("recipe") or ""),
            expected_answer=str(row.get("expected_answer") or row.get("ground_truth") or ""),
            ground_truth_url=str(row.get("ground_truth_url") or gold.get("primary_url") or ""),
            cells=row.get("cells") or gold.get("cells") or [],
            metadata={key: value for key, value in row.items() if key not in known},
        )


class Hit(BaseModel):
    url: str
    title: str = ""
    snippet: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Attempt(BaseModel):
    number: int
    status_code: int | None = None
    latency_ms: int
    ok: bool
    error: str = ""


class HttpAudit(BaseModel):
    method: str
    url: str
    request: dict[str, Any]
    response: Any = None
    ok: bool
    status_code: int | None = None
    error: str = ""
    attempts: list[Attempt] = Field(default_factory=list)
    latency_ms: int
    started_at: str
    ended_at: str


class SearchResult(BaseModel):
    endpoint: str
    surface: Literal["web-search", "news-index"]
    hits: list[Hit] = Field(default_factory=list)
    audit: HttpAudit


class ExtractVerdict(BaseModel):
    answer: str = ""
    cited_url: str = ""


class AccuracyVerdict(BaseModel):
    correct: bool
    cells_hit: int = 0
    note: str = ""


class RecallVerdict(BaseModel):
    bearing_ranks: list[int] = Field(default_factory=list)
    note: str = ""

    @field_validator("bearing_ranks", mode="before")
    @classmethod
    def valid_ranks(cls, value: Any) -> list[int]:
        if not isinstance(value, list):
            return []
        return sorted({int(rank) for rank in value if str(rank).isdigit() and 1 <= int(rank) <= 10})

