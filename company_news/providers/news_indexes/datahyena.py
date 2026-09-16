from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

from company_news.http import request_json
from company_news.models import Case, Hit, SearchResult
from company_news.providers.base import ProviderAdapter, hit
from .common import skipped

RECIPE_INCLUDE = {
    "receives_financing": "funding", "financing_lead": "funding",
    "acquires": "acquisitions", "hires": "exec_moves",
}

TIMELINE = "https://api.datahyena.com/v1/companies/timeline"
MAX_HITS = 10

EVENT_KINDS = {
    "funding": "funding", "acquisition": "acquisitions",
    "execMove": "exec_moves", "exec_move": "exec_moves",
}


def _source_url(record: dict[str, Any], request_url: str) -> str:
    for key in ("sources", "sourceUrls", "articles", "urls", "citations"):
        values = record.get(key) or []
        for value in values if isinstance(values, list) else [values]:
            if isinstance(value, str) and value.startswith("http"):
                return value
            if isinstance(value, dict):
                for field in ("url", "sourceUrl", "href", "link"):
                    if str(value.get(field) or "").startswith("http"):
                        return str(value[field])
    return request_url


def _money(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, (int, float)) and value:
            return f"${value:,.0f}"
    return ""


def _names(records: Any) -> str:
    return ", ".join(
        str(item.get("name")) for item in (records or [])
        if isinstance(item, dict) and item.get("name")
    )


def _sentence(kind: str, record: dict[str, Any]) -> str:
    if kind == "acquisitions":
        acquirer = record.get("acquirer") or {}
        target = record.get("target") or {}
        amount = _money(record, "dealAmountUsd")
        text = (
            f"{acquirer.get('name') or 'Undisclosed acquirer'} acquired "
            f"{target.get('name') or 'undisclosed target'} "
            f"{f'for {amount}' if amount else 'for an undisclosed amount'}"
        )
        if record.get("announcedAt"):
            text += f", announced {record['announcedAt']}"
        text += "."
        if target.get("description"):
            text += f" {target.get('name')}: {target['description']}"
        return text

    if kind == "exec_moves":
        person = record.get("person") or {}
        company = record.get("company") or {}
        text = (
            f"{person.get('name') or 'An executive'} was appointed "
            f"{record.get('role') or 'an executive'} at {company.get('name') or 'the company'}"
        )
        if record.get("fromCompanyName"):
            text += f", joining from {record['fromCompanyName']}"
        date = record.get("effectiveDate") or record.get("announcedAt")
        if date:
            text += f", effective {date}"
        return text + "."

    company = record.get("company") or {}
    amount = _money(record, "amountUsd")
    text = f"{company.get('name') or 'The company'} raised {amount or 'an undisclosed amount'}"
    if record.get("round"):
        text += f" in a {record['round']} round"
    if record.get("announcedAt"):
        text += f", announced {record['announcedAt']}"
    text += "."
    investors = _names(record.get("investors"))
    if investors:
        text += f" Investors: {investors}."
    if company.get("hqCity") or company.get("description"):
        city = company.get("hqCity") or ""
        text += f" {company.get('name')}{f' ({city})' if city else ''}: {company.get('description') or ''}".rstrip()
    return text


def _parse(payload: Any, request_url: str) -> list[Hit]:
    events = (((payload or {}).get("data") or {}).get("events") or [])
    output: list[Hit] = []
    for outer in events[:MAX_HITS]:
        record, resolved = outer, "funding"
        for key, name in EVENT_KINDS.items():
            if isinstance(outer.get(key), dict):
                record, resolved = outer[key], name
                break
        item = hit(_source_url(record, request_url), _sentence(resolved, record), _sentence(resolved, record))
        if item:
            output.append(item)
    return output


class DatahyenaAdapter(ProviderAdapter):
    name = "datahyena"
    surface = "news-index"
    docs_url = "https://datahyena.com/docs"
    required_env = ("DATAHYENA_API_KEY",)

    def _call(self, params: dict[str, str]):
        return request_json(
            "GET", TIMELINE,
            headers={"X-API-Key": os.environ["DATAHYENA_API_KEY"], "Accept": "application/json"},
            params=params, timeout=45,
        )

    def search(self, case: Case) -> SearchResult:
        self.validate_credentials()
        include = RECIPE_INCLUDE.get(case.pattern)
        if not include:
            return skipped(self.name, case, "pattern outside funding / acquisitions / exec_moves")
        name = str(case.metadata.get("company_name") or case.metadata.get("company") or "").strip()
        if not case.company_domain and not name:
            return skipped(self.name, case, "no company identifier available")

        params = {"domain": case.company_domain, "include": include} if case.company_domain else {}
        audit = self._call(params) if params else None
        if (audit is None or audit.status_code == 404) and name:
            params = {"name": name, "include": include}
            audit = self._call(params)
        if audit.status_code == 404:
            audit.ok, audit.error = True, ""

        request_url = f"{TIMELINE}?{urlencode(params)}"
        return SearchResult(
            endpoint=self.name, surface=self.surface,
            hits=_parse(audit.response, request_url) if audit.ok else [], audit=audit,
        )


ADAPTERS = [DatahyenaAdapter()]
