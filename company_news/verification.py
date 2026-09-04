from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import read_json, sha256

SECRET_KEYS = ("authorization", "api-key", "apikey", "api_token", "api-token", "subscription-token")


def _check_redaction(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{path}.{key}"
            if any(part in key.lower() for part in SECRET_KEYS) and child not in (None, "", "***REDACTED***"):
                errors.append(f"unredacted credential-like field: {current}")
            errors.extend(_check_redaction(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_check_redaction(child, f"{path}[{index}]"))
    return errors


def verify_run(run_dir: Path) -> dict[str, int]:
    manifest = read_json(run_dir / "manifest.json")
    errors: list[str] = []
    if sha256(run_dir / "run.json") != manifest.get("run_sha256"):
        errors.append("run.json hash mismatch")
    for record in manifest.get("files") or []:
        path = run_dir / record["path"]
        if not path.is_file():
            errors.append(f"missing file: {record['path']}")
            continue
        if sha256(path) != record["sha256"]:
            errors.append(f"hash mismatch: {record['path']}")
        if record["path"].startswith("audit/"):
            errors.extend(_check_redaction(json.loads(path.read_text()), record["path"]))
    run = read_json(run_dir / "run.json")
    expected = int(run["run"]["case_count"]) * len(run["run"]["endpoints"])
    if int(run.get("cell_count") or 0) != expected:
        errors.append(f"cell count is {run.get('cell_count')}; expected {expected}")
    if errors:
        raise RuntimeError("artifact verification failed:\n- " + "\n- ".join(errors))
    return {"cases": int(run["run"]["case_count"]), "endpoints": len(run["run"]["endpoints"]),
            "cells": int(run["cell_count"]), "files": len(manifest.get("files") or [])}

