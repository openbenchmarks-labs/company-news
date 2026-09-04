from __future__ import annotations

import json
import os
import time
from typing import Any

import boto3
from botocore.config import Config


def model_id() -> str:
    return os.getenv("BEDROCK_JUDGE_MODEL", "us.anthropic.claude-opus-5")


def call_json(system: str, payload: dict[str, Any], *, max_tokens: int) -> tuple[dict[str, Any], dict[str, int]]:
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1",
        config=Config(max_pool_connections=50, retries={"max_attempts": 3, "mode": "adaptive"},
                      read_timeout=180, connect_timeout=10),
    )
    last: Exception | None = None
    response: dict[str, Any] | None = None
    for attempt in range(4):
        try:
            kwargs: dict[str, Any] = {
                "modelId": model_id(),
                "system": [{"text": system}],
                "messages": [{"role": "user", "content": [{"text": json.dumps(payload, ensure_ascii=False)}]}],
                "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.0},
                "additionalModelRequestFields": {"thinking": {"type": "disabled"}},
            }
            try:
                response = client.converse(**kwargs)
            except Exception as exc:  # Some Bedrock profiles reject explicit thinking/temperature.
                if "thinking" not in str(exc).lower() and "temperature" not in str(exc).lower():
                    raise
                kwargs.pop("additionalModelRequestFields", None)
                kwargs["inferenceConfig"].pop("temperature", None)
                response = client.converse(**kwargs)
            break
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < 3:
                time.sleep(min(2 ** attempt, 8))
    if response is None:
        raise RuntimeError(f"Bedrock judge failed: {last}")
    text = "\n".join(
        block.get("text", "")
        for block in response.get("output", {}).get("message", {}).get("content", [])
        if isinstance(block, dict)
    ).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"judge returned no JSON object: {text[:200]}")
    usage = response.get("usage") or {}
    return json.loads(text[start:end + 1]), {
        "input_tokens": int(usage.get("inputTokens") or 0),
        "output_tokens": int(usage.get("outputTokens") or 0),
    }

