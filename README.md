# Company News Search Benchmark

Open, independent benchmark of company news APIs for AI agents. General web
search APIs and dedicated news indexes answer the same 300 company-news
questions, one query each, no query rewrite and no page fetch, scored on
extracted-answer accuracy and ranked by cost per 1,000 correct answers. Web
search: Exa, Parallel, Perplexity, Linkup, Firecrawl, Brave Search, You, Nimble,
TinyFish, Tavily, String, and a Google SERP API. News indexes: Seltz,
PredictLeads, Autobound, and Datahyena. Open source code + open data.

**Live leaderboard:** https://openbenchmarks.com/company-news
**Public dataset:** [`openbenchmarks/OB-News-Websearch`](https://huggingface.co/datasets/openbenchmarks/OB-News-Websearch)

Published by **[OpenBenchmarks Labs](https://openbenchmarks.com)**. No vendor
sponsors or controls this benchmark.

This repo is **runner and evaluation code only**. It does not bundle a dataset,
run dumps, raw vendor HTTP, or leaderboard snapshots.

Table updated **2026-09-15** on the private held-out set of 300 questions.
The live board is the source of truth and moves with each run.

## Which API is best for company news?

Ranked by **$ / 1k correct**: the list price of 1,000 queries divided by
extracted-answer accuracy, which is what you pay for 1,000 right answers.
Accuracy alone ignores the bill and raw cost per query ignores misses, so
cost-to-quality is the number that compounds when an agent fires this call all
day.

The two kinds of API are banded and ranked inside each band. A single ranking
would claim they are substitutes.

**Web search APIs.** **TinyFish** is free at 92.0% accuracy, capped at 30
requests/min and 500/hour, so $0 is not unlimited throughput. The best-value paid
row is **Parallel (mode=fast)** at $1.16 per 1,000 correct. The most accurate
row, **Exa (type=fast)** at 99.3%, costs $7.05 per 1,000 correct.

| # | Vendor | Endpoint | $ / 1k correct | Accuracy | AR@1 | AR@5 | Latency | Snippet tokens |
|---|---|---|---|---|---|---|---|---|
| 1 | TinyFish | GET api.search.tinyfish.ai | Free (30 req/min) | 92.0% | 74.3% | 90.7% | 2.62s | 441 |
| 1 | Parallel fast | POST /v1/search mode=fast | $1.16 | 86.0% | 44.3% | 79.0% | 942ms | 1,839 |
| 2 | Parallel turbo | POST /v1/search mode=turbo | $1.40 | 71.3% | 45.3% | 66.0% | 348ms | 1,853 |
| 3 | Nimble | POST /v2/search search_depth=lite · focus=general  | $1.46 | 75.3% | 64.0% | 75.3% | 3.15s | 413 |
| 4 | SERP (RapidAPI) | GET google-search74 limit=10 | $3.13 | 96.0% | 78.0% | 95.0% | 751ms | 497 |
| 5 | Perplexity (low) | POST /search context=low | $5.14 | 97.3% | 91.7% | 98.3% | 1.38s | 476 |
| 6 | Linkup fast | POST /v1/search depth=fast | $5.17 | 96.7% | 79.0% | 94.7% | 1.57s | 3,022 |
| 7 | Firecrawl | POST /v2/search | $5.24 | 95.3% | 77.7% | 96.7% | 510ms | 678 |
| 8 | Nimble | POST /v2/search search_depth=lite · focus=news | $5.24 | 21.0% | 10.3% | 23.0% | 2.19s | 237 |
| 9 | Brave LLM Context | POST /res/v1/llm/context | $5.32 | 94.0% | 81.0% | 94.7% | 601ms | 2,064 |
| 10 | Parallel basic | POST /v1/search mode=basic | $5.36 | 93.3% | 55.0% | 92.0% | 1.68s | 2,330 |
| 11 | Brave Search | GET /res/v1/web/search count=10 | $5.36 | 93.3% | 79.3% | 91.7% | 630ms | 817 |
| 12 | Nimble | POST /v2/search search_depth=standard · focus=general | $5.38 | 93.0% | 86.3% | 94.3% | 861ms | 2,730 |
| 13 | Linkup standard | POST /v1/search depth=standard | $5.43 | 92.0% | 67.3% | 90.3% | 2.55s | 2,983 |
| 14 | You | POST /v1/search extraction_mode=highlights · knowledge=core | $5.43 | 92.0% | 67.3% | 89.7% | 889ms | 2,862 |
| 15 | You | POST /v1/search extraction_mode=highlights | $5.51 | 90.7% | 72.0% | 89.7% | 628ms | 2,837 |
| 16 | Exa fast | POST /search type=fast | $7.05 | 99.3% | 95.0% | 99.3% | 652ms | 1,987 |
| 17 | Exa instant | POST /search type=instant | $7.17 | 97.7% | 80.0% | 97.3% | 398ms | 2,128 |
| — | Tavily basic | POST /search search_depth=basic | Pending | Pending | Pending | Pending | Pending | Pending |
| — | Tavily advanced | POST /search search_depth=advanced | Pending | Pending | Pending | Pending | Pending | Pending |
| — | String | POST /v1/search engine=google | Pending | Pending | Pending | Pending | Pending | Pending |

Tavily basic, Tavily advanced, and String are in the current roster; benchmark
results are pending.

**News index and company-event APIs.** **Seltz (scope=news)** is the strongest
dedicated index at $8.57 per 1,000 correct and 58.3% accuracy. The three
domain-keyed event APIs are priced per credit and answer a minority of the
questions, so their cost per correct answer runs from $121 to $716.

| # | Vendor | Endpoint | $ / 1k correct | Accuracy | AR@1 | AR@5 | Latency | Snippet tokens |
|---|---|---|---|---|---|---|---|---|
| 1 | Seltz news | POST /v1/search scope=news | $8.57 | 58.3% | 44.3% | 60.0% | 403ms | 2,919 |
| 2 | Autobound news events | POST /v1/companies/enrich signal_types=news | $120.76 | 30.0% | 21.0% | 25.0% | 146ms | 879 |
| 3 | PredictLeads news events | GET /api/v3/companies/{domain}/news_events categories[] | $193.52 | 20.7% | 14.0% | 20.0% | 398ms | 484 |
| 4 | Datahyena company events | GET /v1/companies/timeline include=funding,acquisitions,exec_moves | $716.07 | 5.3% | 5.3% | 6.7% | 187ms | 22 |

Cost per 1,000 queries is the published pay-as-you-go list price, not promotional
packs or volume discounts. Autobound and Datahyena are converted from credits
(Starter $19 / 2,000 credits and PAYG $25 / 500 credits). Pricing assumptions
and their effective date are versioned in `company_news/pricing.py`.

Full ranking, both bands: https://openbenchmarks.com/company-news

## Do dedicated news APIs beat web search for company news?

Not on this run. On identical questions, query, result cap and judge, the best
general web search endpoint is free (TinyFish) and the best paid one is $1.16
per 1,000 correct (Parallel fast). The strongest dedicated news index, Seltz, is
$8.57 per 1,000 correct at 58.3% accuracy. Fourteen of the eighteen measured web search
rows shown above score above 90%. No news index reaches 60%.

The gap is mechanism, not freshness. Every question is a recent event pinned to
an official wire or newsroom URL, which is the content a news index is built to
carry. The domain-keyed event APIs (PredictLeads, Autobound, Datahyena) lose most
questions at the lookup stage: the event is not in the index under that domain
and category, so nothing comes back to extract from.

Dedicated news indexes on this task: https://openbenchmarks.com/company-news/news-index-apis
Web search APIs on this task: https://openbenchmarks.com/company-news/web-search-apis

## Which web search API is most accurate for company news?

**Exa (type=fast)** leads at 99.3% extracted-answer accuracy, followed by Exa
instant at 97.7%, Perplexity (low) at 97.3%, Linkup fast at 96.7% and the Google
SERP API at 96.0%. Exa fast also leads answer recall, with the correct answer
already in the first snippet 95.0% of the time.

Accuracy is tightly bunched: fourteen of eighteen measured web search rows shown above land between
90% and 99.3%. On a one-query lookup the interesting spread is cost and latency,
not accuracy.

**Model-only baseline: 0.** Every question is a company event dated after the
extractor's training cutoff, so a correct answer has to be found in the returned
snippets rather than recalled.

## Which company news API is fastest?

**Parallel turbo** returns in 348ms mean at 71.3% accuracy. The quickest endpoint that is also accurate is
**Exa instant**: 398ms at 97.7%. Among the news indexes, Autobound answers in
146ms and Seltz in 403ms.

Latency is client-observed HTTP duration for the search call only, measured from
one client at case concurrency one. Extraction and judging are not included.

## Which company news API is most token-efficient?

Measured as accuracy per 1,000 snippet tokens returned, so higher means more
correct lookups per token of LLM context. **TinyFish** leads at 208 (441 tokens
per query at 92.0%), then **Perplexity (low)** at 205 (476 tokens at 97.3%) and
the **Google SERP API** at 193 (497 tokens at 96.0%). The accuracy leader, Exa
fast, returns 1,987 tokens per query for a score of 50. That difference lands in
the context window on every call an agent makes.

## How it is scored

- **Accuracy:** percentage of all cases whose extracted answer contains every
  gold cell. The extractor is `gpt-5.6-terra` at medium reasoning and sees only
  normalized URL, title, and snippet fields. It never fetches the page.
- **AR@1 / AR@5 / AR@10:** answer-bearing recall. Percentage of cases where at
  least one result within the first K positions contains every gold cell in its
  snippet.
- **Source recall@5:** percentage of cases where the locked official URL, or an
  equivalent official copy, appears in the first five results.
- **Snippet tokens:** approximate normalized context returned by the endpoint.
- **Latency:** client-observed HTTP duration. Aggregated latency excludes
  unsuccessful HTTP requests and reports the successful-request count beside the
  total.
- **Cost per 1,000 correct:** endpoint list price per query divided by measured
  accuracy.

Accuracy and answer-bearing recall are judged by `claude-opus-5` through Amazon
Bedrock against human-reviewed gold. Gold is one atomic fact (amount, person,
acquirer, location, product, headcount) locked from an official Business Wire,
PR Newswire, GlobeNewswire, or company newsroom page. Questions never name the
gold cell. Operational failures remain visible: accuracy always uses all
submitted cases as its denominator.

## Fixed protocol

- One unchanged company-news question per case.
- One request per endpoint configuration.
- At most 10 returned results.
- No query rewriting, pagination, follow-up search, or linked-page fetching.
- Cases execute sequentially; all selected providers for a case are called
  concurrently, and the evaluator waits for every provider call in the round
  before advancing.
- General web search APIs receive only the question. Domain-keyed event APIs
  also receive the resolved company domain and the event recipe, because that is
  the only way to call them.
- Credentials are redacted before HTTP audit artifacts are written.

## Published endpoint roster

The default roster contains 25 endpoint configurations.

**Web search:** Parallel turbo, fast, and basic; Exa instant and fast; Brave Web
Search and LLM Context; You highlights with and without `knowledge=core`; Nimble
lite/general, lite/news, and standard; Perplexity low context; TinyFish;
Firecrawl; Tavily basic and advanced; Google Search through RapidAPI; Linkup
fast and standard; and String Web Access.

**News indexes:** PredictLeads category-filtered news events, Datahyena company
events, Autobound news events, and Seltz News Search.

Stable endpoint IDs, as accepted by `--endpoints`:

```text
parallel_turbo parallel_fast parallel_basic exa_instant exa_fast
nimble_lite nimble_lite_news nimble_standard
brave brave_llm you_highlights you_highlights_core perplexity_low tinyfish firecrawl
tavily_basic tavily_advanced serp linkup_fast linkup_standard string
predictleads_category datahyena autobound seltz_news
```

Run `company-news list-providers` to see surface assignments and official
documentation links.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

Populate only the credentials for the endpoints you select. OpenAI and
AWS/Bedrock credentials are required for evaluation. A search-only run does not
need AWS credentials; it still needs OpenAI when the PredictLeads arm is
selected, because that adapter maps each question to a closed set of event
categories with the benchmark extractor model.

## Dataset contract

The runner accepts either a JSON array or an object containing `cases`,
`samples`, or `items`. Every case requires:

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

`company_domain` and `pattern` are necessary for domain-keyed company-event
indexes. General web search APIs receive only `question`. The public eval set on
Hugging Face uses this contract. See [DATA.md](DATA.md) for the complete
artifact contract.

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

## Related benchmarks

This is the factual-lookup task of the OpenBenchmarks web search benchmark. The
same web search vendors are measured on two other jobs:

- **Hard retrieval.** Coding-agent tickets against enterprise docs, scored on
  grounded task completion: https://openbenchmarks.com/web-search-for-coding-agents
  (code: [web-search-for-coding-agents](https://github.com/openbenchmarks-labs/web-search-for-coding-agents))
- **Multi-hop search.** Multi-constraint company discovery, scored on F1:
  https://openbenchmarks.com/multi-turn-company-search
  (code: [multi-turn-company-search](https://github.com/openbenchmarks-labs/multi-turn-company-search))
- **Web search APIs only on this task**, without the news index band:
  [factual-lookup-company-news-search](https://github.com/openbenchmarks-labs/factual-lookup-company-news-search)
- **Methodology and all three boards:** https://openbenchmarks.com/web-search
- **Agent-readable index:** https://openbenchmarks.com/llms.txt

## Changelog

- **2026-09-15.** Added Nimble Search lite/general, lite/news, and standard/general to the existing table and runner roster. All use `full_content=false`, 10 results, and descriptions only; no Extract call. Added You highlights + `knowledge=core` on the 300-question Company News benchmark; published accuracy is 92.0%, versus 90.7% with highlights alone. Updated the You roster and request contracts.

## License

MIT.
