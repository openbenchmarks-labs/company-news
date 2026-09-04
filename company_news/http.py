from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from .models import Attempt, HttpAudit

RETRYABLE = {429, 500, 502, 503, 504}
SECRET_HEADER_PARTS = ("authorization", "key", "token", "secret", "password")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        key: "***REDACTED***" if any(part in key.lower() for part in SECRET_HEADER_PARTS) else value
        for key, value in headers.items()
    }


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 60,
    max_attempts: int = 4,
) -> HttpAudit:
    started = time.perf_counter()
    started_at = now()
    attempts: list[Attempt] = []
    payload: Any = None
    status: int | None = None
    error = ""
    ok = False

    for index in range(max_attempts):
        attempt_started = time.perf_counter()
        try:
            response = requests.request(
                method, url, headers=headers, params=params, json=body, timeout=timeout
            )
            status = response.status_code
            try:
                payload = response.json()
            except ValueError:
                payload = {"_raw": (response.text or "")[:8000]}
            elapsed = round((time.perf_counter() - attempt_started) * 1000)
            ok = response.ok
            error = "" if ok else f"HTTP {status}: {str(payload)[:400]}"
            attempts.append(Attempt(number=index + 1, status_code=status, latency_ms=elapsed, ok=ok, error=error))
            if ok or status not in RETRYABLE or index + 1 == max_attempts:
                break
            time.sleep(min(2 ** index, 8))
        except requests.RequestException as exc:
            elapsed = round((time.perf_counter() - attempt_started) * 1000)
            error = f"{type(exc).__name__}: {exc}"
            attempts.append(Attempt(number=index + 1, latency_ms=elapsed, ok=False, error=error))
            if index + 1 == max_attempts:
                break
            time.sleep(min(2 ** index, 8))

    return HttpAudit(
        method=method,
        url=url,
        request={"headers": redact_headers(headers), "body": body, "params": params},
        response=payload,
        ok=ok,
        status_code=status,
        error=error,
        attempts=attempts,
        latency_ms=round((time.perf_counter() - started) * 1000),
        started_at=started_at,
        ended_at=now(),
    )

