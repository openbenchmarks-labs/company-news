from company_news.models import Case


def test_case_accepts_legacy_gold_shape():
    case = Case.from_record({
        "id": "one", "question": "What happened?", "recipe": "hires",
        "gold": {"domain": "example.com", "primary_url": "https://example.com/news",
                 "cells": [{"label": "person", "value": "Ada"}]},
        "ground_truth": "Ada was hired",
    })
    assert case.company_domain == "example.com"
    assert case.pattern == "hires"
    assert case.cells[0].value == "Ada"

