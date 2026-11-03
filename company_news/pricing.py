"""Public list-price assumptions. Update the effective date with every change."""

PRICE_EFFECTIVE_DATE = "2026-11-02"

USD_PER_REQUEST = {
    # Context Developer top-up: $2.20 / 1,000 credits; 2 credits / 10 results with Highlights.
    # https://www.context.dev/pricing (2026-10-20)
    "context": 0.0044,
    "hydrafetch": 0.00127,
    "nimble_lite": 0.0011,
    "nimble_lite_news": 0.0011,
    "nimble_standard": 0.005,
    "parallel_turbo": 0.001,
    "parallel_fast": 0.001,
    "parallel_basic": 0.005,
    "exa_instant": 0.007,
    "exa_fast": 0.007,
    "brave": 0.005,
    "brave_llm": 0.005,
    "you_highlights_core": 0.005,
    "you_highlights": 0.005,
    "perplexity_low": 0.005,
    "tinyfish": 0.0,
    "firecrawl": 0.005,
    "predictleads_category": 0.040,
    "datahyena": 0.050,
    "autobound": 0.019,
    "seltz_news": 0.005,
    # https://docs.tavily.com/documentation/api-credits (1 / 2 PAYG credits).
    "tavily_basic": 0.008,
    "tavily_advanced": 0.016,
    "serp": 0.003,
    "linkup_fast": 0.005,
    "linkup_standard": 0.005,
}

