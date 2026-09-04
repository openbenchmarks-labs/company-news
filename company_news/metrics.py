from __future__ import annotations

from collections import defaultdict
from statistics import mean, median
from typing import Any
from urllib.parse import urlparse

from .pricing import USD_PER_REQUEST


def _pct(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 2) if denominator else 0.0


def _tokens(text: str) -> int:
    return max(1, round(len(" ".join((text or "").split())) / 4)) if text.strip() else 0


def _url_key(url: str) -> str:
    parsed = urlparse(url or "")
    return f"{parsed.netloc.lower().removeprefix('www.')}{parsed.path.rstrip('/')}"


def aggregate(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell in cells:
        grouped[cell["endpoint"]].append(cell)
    rows: list[dict[str, Any]] = []
    for endpoint, items in grouped.items():
        correct = sum(bool((item.get("evaluation") or {}).get("accuracy", {}).get("correct")) for item in items)
        succeeded = [item for item in items if item.get("ok")]
        latencies = [float(item.get("latency_ms") or 0) for item in succeeded]
        ar = lambda k: sum(bool((item.get("evaluation") or {}).get("answer_recall", {}).get(f"ar{k}")) for item in items)
        source5 = 0
        snippet_tokens: list[int] = []
        for item in items:
            gold = _url_key(item.get("ground_truth_url") or "")
            hits = item.get("hits") or []
            if gold and any(_url_key(hit.get("url") or "") == gold for hit in hits[:5]):
                source5 += 1
            snippet_tokens.append(sum(_tokens(f"{hit.get('title', '')} {hit.get('snippet', '')}") for hit in hits))
        accuracy = correct / len(items) if items else 0
        unit = USD_PER_REQUEST.get(endpoint, 0.0)
        rows.append({
            "endpoint": endpoint,
            "surface": items[0].get("surface"),
            "total_cases": len(items),
            "successful_requests": len(succeeded),
            "correct": correct,
            "accuracy_pct": _pct(correct, len(items)),
            "answer_recall_1_pct": _pct(ar(1), len(items)),
            "answer_recall_5_pct": _pct(ar(5), len(items)),
            "answer_recall_10_pct": _pct(ar(10), len(items)),
            "source_recall_5_pct": _pct(source5, len(items)),
            "mean_snippet_tokens": round(mean(snippet_tokens), 1) if snippet_tokens else 0,
            "mean_latency_ms": round(mean(latencies), 1) if latencies else None,
            "median_latency_ms": round(median(latencies), 1) if latencies else None,
            "list_price_per_query_usd": unit,
            "cost_per_1000_correct_usd": round(unit * 1000 / accuracy, 2) if accuracy else None,
        })
    return sorted(rows, key=lambda row: (row["surface"], row["cost_per_1000_correct_usd"] is None,
                                         row["cost_per_1000_correct_usd"] or 0, row["endpoint"]))

