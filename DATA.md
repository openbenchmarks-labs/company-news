# Dataset and artifact contracts

No dataset or generated run is committed to this repository. Paths below describe files created in the caller-selected `--output` directory.

## Input dataset

The input is a JSON array, or an object with an array under `cases`, `samples`, or `items`.

Required fields:

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable, unique case identifier. |
| `question` | string | Exact natural-language query sent to general search endpoints. |

Evaluation fields:

| Field | Type | Purpose |
|---|---|---|
| `expected_answer` | string | Human-readable reference answer. |
| `cells` | array | Atomic values that must all be present for exact correctness. |
| `ground_truth_url` | string | Locked source URL used for source recall. |

Product-shaped index fields:

| Field | Type | Purpose |
|---|---|---|
| `company_domain` | string | Company identifier for domain-keyed APIs. |
| `pattern` | string | Closed event recipe used to select supported event categories. |

For compatibility, `ground_truth`, `recipe`, and nested `gold.cells`, `gold.domain`, and `gold.primary_url` are accepted aliases.

## Output layout

```text
<run-dir>/
├── run-plan.json
├── run.json
├── manifest.json
├── cells/<case-id>/<endpoint>.json
└── audit/<case-id>/<endpoint>.json
```

`run-plan.json` freezes the dataset path and hash, selected endpoint IDs, case count, concurrency, result cap, and start time.

Each cell records:

- Case identity and locked reference fields
- Endpoint and surface
- HTTP success, status, error, and client-observed latency
- Up to 10 normalized hits
- Extracted answer and citation
- Accuracy verdict
- AR@1, AR@5, AR@10 and answer-bearing ranks
- Extractor and judge identities and token usage
- Relative path to the redacted HTTP audit envelope

`run.json` contains the run plan, all cells, and aggregate leaderboard rows. `manifest.json` contains SHA-256 hashes for the run, cells, and audit envelopes.

## Redaction

Authorization, API key, subscription token, and similar credential-bearing HTTP headers are replaced with `***REDACTED***` before being written. Response bodies are retained because they are necessary to audit normalization and scoring. Review provider terms and the output before publishing a run.

## Denominators

Accuracy and recall metrics divide by every submitted case. A provider failure is therefore not silently removed from quality metrics. HTTP latency aggregates use successful requests and report their successful-request count beside the total case count.

