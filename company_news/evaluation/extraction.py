from __future__ import annotations

import json
import os
import time
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from company_news.models import Case, ExtractVerdict, Hit

T = TypeVar("T", bound=BaseModel)

EXTRACT_PROMPT = (
    "Answer only from the provided search snippets. No extra research. "
    "If the snippets do not contain the fact, answer empty. Do not use outside knowledge."
)


def parse_openai(system: str, payload: dict, schema: type[T]) -> tuple[T, dict[str, int]]:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], max_retries=0, timeout=180)
    model = os.getenv("EXTRACT_MODEL", "gpt-5.6-terra")
    effort = os.getenv("EXTRACT_REASONING_EFFORT", "medium")
    last: Exception | None = None
    for attempt in range(3):
        try:
            response = client.responses.parse(
                model=model,
                reasoning={"effort": effort},
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                text_format=schema,
                max_output_tokens=4000,
                store=False,
            )
            if response.output_parsed is None:
                raise RuntimeError("extractor returned no parsed output")
            usage = response.usage
            return response.output_parsed, {
                "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
                "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
            }
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"extractor failed after three attempts: {last}")


def extract(case: Case, hits: list[Hit]) -> tuple[ExtractVerdict, dict[str, int]]:
    if not hits:
        return ExtractVerdict(), {"input_tokens": 0, "output_tokens": 0}
    packed = [{"url": row.url, "title": row.title, "snippet": row.snippet} for row in hits[:10]]
    return parse_openai(EXTRACT_PROMPT, {"question": case.question, "results": packed}, ExtractVerdict)

