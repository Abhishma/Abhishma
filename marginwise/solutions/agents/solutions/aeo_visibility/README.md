# AEO Visibility: AI assistant share of voice tracking

## What it does
A prompt harness that asks AI assistants (Claude, ChatGPT, Perplexity) a fixed set of buying questions per category and market, parses which brands are named, in what order and list rank, with sentiment, and scores share of voice, mention rate and average position per brand and per assistant. An analyst agent turns the scores into a monthly report with evidence-based actions.

Components:
- fixtures/questions.json: question templates (local services, ecommerce products; English, German, Arabic)
- parser.py: deterministic mention parser and share-of-voice scoring (tested on fixture answers)
- harness.py: builds questions and runs them across adapters
- adapters.py: FixtureAdapter (offline), AnthropicAdapter (Messages API with web search), OpenAI and Perplexity stubs (TODO)

## Integrations
Anthropic API (implemented), OpenAI and Perplexity APIs (stubs), Google Sheets / Looker Studio for trend dashboards, Google Business Profile and review platforms for actions.

## KPIs
- Client share of voice across assistants (monthly trend)
- Mention rate on high-intent questions (emergency, "best", "near me")
- Average position when named
- Negative mentions (target: 0)

## Setup
1. Define tracked brands with aliases (brands.json) and the client's categories and markets.
2. Choose question sets and fill values; add client-specific questions.
3. Implement OpenAI and Perplexity adapters; set API keys; schedule monthly runs (3 repeats recommended, answers vary).
4. Store run outputs to trend month over month.

## Guardrails
- Numbers come only from the deterministic parser; the report writer cannot invent them.
- Refuses fake reviews, review gating, and AI prompt-injection tactics.
- Results presented as a sample, not guarantees.

## Price (USD)
$1,500-4,000/month (retainer, includes reporting and recommended actions).
