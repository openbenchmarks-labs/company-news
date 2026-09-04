from __future__ import annotations

import os
from typing import Any

from company_news.models import Case, SearchResult
from .bedrock import model_id
from .extraction import extract
from .judging import judge_accuracy, judge_recall


def evaluate_search_result(case: Case, result: SearchResult) -> dict[str, Any]:
    if not result.audit.ok:
        extracted, extract_tokens = extract(case, [])
    else:
        extracted, extract_tokens = extract(case, result.hits)
    accuracy, accuracy_tokens = judge_accuracy(case, extracted)
    recall, recall_tokens = judge_recall(case, result.hits if result.audit.ok else [])
    ranks = recall.bearing_ranks
    return {
        "extract": extracted.model_dump(),
        "accuracy": accuracy.model_dump(),
        "answer_recall": {
            **recall.model_dump(),
            "ar1": any(rank <= 1 for rank in ranks),
            "ar5": any(rank <= 5 for rank in ranks),
            "ar10": any(rank <= 10 for rank in ranks),
        },
        "models": {
            "extractor": os.getenv("EXTRACT_MODEL", "gpt-5.6-terra"),
            "extractor_reasoning": os.getenv("EXTRACT_REASONING_EFFORT", "medium"),
            "judge": "claude-opus-5",
            "judge_model_id": model_id(),
            "judge_transport": "bedrock-converse",
        },
        "tokens": {"extract": extract_tokens, "accuracy": accuracy_tokens, "answer_recall": recall_tokens},
    }

