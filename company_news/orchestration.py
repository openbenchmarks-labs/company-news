from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .artifacts import load_cases, read_json, sha256, write_json
from .evaluation import evaluate_search_result
from .metrics import aggregate
from .models import Case, SearchResult
from .providers import selected_adapters


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _cell_path(run_dir: Path, case_id: str, endpoint: str) -> Path:
    return run_dir / "cells" / case_id / f"{endpoint}.json"


def _audit_path(run_dir: Path, case_id: str, endpoint: str) -> Path:
    return run_dir / "audit" / case_id / f"{endpoint}.json"


def _cell(case: Case, result: SearchResult, evaluation: dict[str, Any] | None, audit_path: Path) -> dict[str, Any]:
    return {
        "case_id": case.id,
        "question": case.question,
        "company_domain": case.company_domain,
        "pattern": case.pattern,
        "expected_answer": case.expected_answer,
        "ground_truth_url": case.ground_truth_url,
        "cells": [item.model_dump() for item in case.cells],
        "endpoint": result.endpoint,
        "surface": result.surface,
        "ok": result.audit.ok,
        "status_code": result.audit.status_code,
        "error": result.audit.error,
        "latency_ms": result.audit.latency_ms,
        "started_at": result.audit.started_at,
        "ended_at": result.audit.ended_at,
        "hits": [item.model_dump() for item in result.hits],
        "audit_path": str(audit_path),
        "evaluation": evaluation,
    }


def run_benchmark(
    dataset: Path,
    output: Path | None,
    *,
    endpoints: list[str] | None = None,
    limit: int = 0,
    search_only: bool = False,
    resume: bool = False,
) -> Path:
    load_dotenv(".env")
    run_dir = output or Path("runs") / _stamp()
    cases = [Case.from_record(row) for row in load_cases(dataset)]
    if limit:
        cases = cases[:limit]
    adapters = selected_adapters(endpoints)
    for adapter in adapters:
        adapter.validate_credentials()
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "run-plan.json", {
        "dataset": str(dataset.resolve()),
        "dataset_sha256": sha256(dataset),
        "case_count": len(cases),
        "endpoints": [adapter.name for adapter in adapters],
        "case_concurrency": 1,
        "provider_calls_within_case": "parallel",
        "max_results": 10,
        "search_only": search_only,
        "started_at": datetime.now(timezone.utc).isoformat(),
    })

    for case_number, case in enumerate(cases, 1):
        pending = [adapter for adapter in adapters if not (resume and _cell_path(run_dir, case.id, adapter.name).exists())]
        fetched: dict[str, SearchResult] = {}
        with ThreadPoolExecutor(max_workers=max(1, len(pending))) as pool:
            futures = {pool.submit(adapter.search, case): adapter.name for adapter in pending}
            for future in as_completed(futures):
                fetched[futures[future]] = future.result()

        def finish(endpoint: str) -> tuple[str, dict[str, Any]]:
            result = fetched[endpoint]
            audit_file = _audit_path(run_dir, case.id, endpoint)
            write_json(audit_file, result.audit.model_dump())
            evaluation = None if search_only else evaluate_search_result(case, result)
            return endpoint, _cell(case, result, evaluation, audit_file.relative_to(run_dir))

        if fetched:
            with ThreadPoolExecutor(max_workers=len(fetched)) as pool:
                futures = [pool.submit(finish, endpoint) for endpoint in fetched]
                for future in as_completed(futures):
                    endpoint, payload = future.result()
                    write_json(_cell_path(run_dir, case.id, endpoint), payload)
        print(f"[{case_number}/{len(cases)}] {case.id}: {len(pending)} endpoint(s)", flush=True)

    build_snapshot(run_dir)
    return run_dir


def _all_cells(run_dir: Path) -> list[dict[str, Any]]:
    return [read_json(path) for path in sorted((run_dir / "cells").glob("*/*.json"))]


def evaluate_run(run_dir: Path, *, workers: int = 4) -> None:
    load_dotenv(".env")
    paths = sorted((run_dir / "cells").glob("*/*.json"))

    def evaluate(path: Path) -> tuple[Path, dict[str, Any]]:
        cell = read_json(path)
        if cell.get("evaluation"):
            return path, cell
        case = Case(
            id=cell["case_id"], question=cell["question"], company_domain=cell.get("company_domain", ""),
            pattern=cell.get("pattern", ""), expected_answer=cell.get("expected_answer", ""),
            ground_truth_url=cell.get("ground_truth_url", ""), cells=cell.get("cells") or [],
        )
        audit = read_json(run_dir / cell["audit_path"])
        result = SearchResult(
            endpoint=cell["endpoint"], surface=cell["surface"], hits=cell.get("hits") or [], audit=audit,
        )
        cell["evaluation"] = evaluate_search_result(case, result)
        return path, cell

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for path, cell in [future.result() for future in as_completed([pool.submit(evaluate, path) for path in paths])]:
            write_json(path, cell)
    build_snapshot(run_dir)


def build_snapshot(run_dir: Path) -> dict[str, Any]:
    cells = _all_cells(run_dir)
    plan = read_json(run_dir / "run-plan.json")
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run": plan,
        "cell_count": len(cells),
        "leaderboard": aggregate(cells),
        "cells": cells,
    }
    write_json(run_dir / "run.json", payload)
    manifest = {
        "schema_version": 1,
        "run_sha256": sha256(run_dir / "run.json"),
        "files": [
            {"path": str(path.relative_to(run_dir)), "sha256": sha256(path)}
            for path in sorted([*(run_dir / "cells").glob("*/*.json"), *(run_dir / "audit").glob("*/*.json")])
        ],
    }
    write_json(run_dir / "manifest.json", manifest)
    return payload

