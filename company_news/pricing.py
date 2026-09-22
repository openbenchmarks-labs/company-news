"""Public list-price assumptions. Update the effective date with every change."""

PRICE_EFFECTIVE_DATE = "2026-09-15"

USD_PER_REQUEST = {
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
    # https://portal.usestring.ai/docs/get-started/pricing (search, Starter $1.50 / 1,000;
    # the $20/mo plan fee is not in the per-query rate).
    "string": 0.0015,
}

