# OpenBenchmarks Company News Benchmark

Open runner for the [OpenBenchmarks Company News Search Benchmark](https://openbenchmarks.com/company-news).

The benchmark asks one atomic company-news question at a time and compares two different product surfaces under the same protocol:

- **General web-search APIs**, which search the open web from a natural-language query.
- **News indexes and company-event APIs**, which expose news or structured company events through product-specific lookup surfaces.

The surfaces share questions and evaluation, but should be reported in separate bands. A news index is not presented as a general web-search API.

This repository deliberately contains **runner and evaluation code only**. It does not bundle a dataset or run artifacts. The public dataset is available on Hugging Face at **[openbenchmarks/OB-News-Websearch](https://huggingface.co/datasets/openbenchmarks/OB-News-Websearch)**.

## Fixed protocol

- One unchanged company-news question per case.
- One request per endpoint configuration.
- At most 10 returned results.
- No query rewriting, pagination, follow-up search, or linked-page fetching.
- Cases execute sequentially; all selected providers for a case are called concurrently.
- The evaluator waits for every provider call in the round before advancing.
- The extractor sees only normalized URL, title, and snippet fields.
- Extractor: `gpt-5.6-terra`, medium reasoning.
- Accuracy and answer-bearing recall judge: `claude-opus-5` through Amazon Bedrock.
- Credentials are redacted before HTTP audit artifacts are written.

## Published endpoint roster

The default roster contains 20 endpoint configurations:

**Web search:** Parallel turbo, fast, and basic; Exa instant and fast; Brave Web Search and LLM Context; You Search and You highlights; Perplexity low context; TinyFish; Firecrawl; Tavily ultra-fast; Google Search through RapidAPI; and Linkup fast and standard.

**News indexes:** PredictLeads category-filtered news events, DataHyena company events, Autobound news events, and Seltz News Search.

Run `company-news list-providers` to see stable endpoint IDs, surface assignments, and official documentation links.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

Populate only the credentials for the endpoints you select. OpenAI and AWS/Bedrock credentials are required for evaluation. A search-only run does not need AWS credentials; it still needs OpenAI when the PredictLeads arm is selected because that product-shaped adapter maps each question to a closed set of event categories with the benchmark extractor model.

## Dataset contract

The runner accepts either a JSON array or an object containing `cases`, `samples`, or `items`. Every case requires:

```json
{
  "id": "stable-case-id",
  "question": "How much did Example Corp raise in its latest round?",
  "company_domain": "example.com",
  "pattern": "receives_financing",
  "expected_answer": "$25 million",
  "ground_truth_url": "https://example.com/news/...",
  "cells": [{"label": "amount", "value": "$25 million"}]
}
```

`company_domain` and `pattern` are necessary for product-shaped company-event indexes. General web-search APIs receive only `question`. See [DATA.md](DATA.md) for the complete artifact contract.

## Run it

List providers:

```bash
company-news list-providers
```

One-case smoke test against two endpoints:

```bash
company-news run \
  --dataset /path/to/company-news-samples.json \
  --output runs/smoke \
  --limit 1 \
  --endpoints exa_instant,seltz_news
```

Full default-roster run:

```bash
company-news run \
  --dataset /path/to/company-news-samples.json \
  --output runs/full
```

Resume without recalling completed case/endpoint cells:

```bash
company-news run \
  --dataset /path/to/company-news-samples.json \
  --output runs/full \
  --resume
```

Separate vendor calls from paid model evaluation:

```bash
company-news run \
  --dataset /path/to/company-news-samples.json \
  --output runs/full \
  --search-only

company-news evaluate --run-dir runs/full --workers 4
```

Verify counts, hashes, and credential redaction:

```bash
company-news verify --run-dir runs/full
```

Bare Python wrappers are also available:

```bash
python scripts/run_company_news_benchmark.py --dataset /path/to/samples.json --limit 1
python scripts/evaluate_run.py --run-dir runs/full
python scripts/build_public_snapshot.py --run-dir runs/full
python scripts/verify_public_artifacts.py --run-dir runs/full
```

## Metrics

- **Accuracy:** percentage of all cases whose extracted answer contains every gold cell.
- **AR@1 / AR@5 / AR@10:** percentage where at least one result within the first K positions contains every gold cell in its snippet.
- **Source recall@5:** percentage where the locked source URL appears in the first five results.
- **Snippet tokens:** approximate normalized context returned by the endpoint.
- **Latency:** client-observed HTTP duration. Aggregated latency excludes unsuccessful HTTP requests.
- **Cost per 1,000 correct:** endpoint list price per query divided by measured accuracy. Pricing assumptions are versioned in `company_news/pricing.py`.

Operational failures remain visible and accuracy always uses all submitted cases as its denominator.


No vendor sponsors or controls this benchmark.
