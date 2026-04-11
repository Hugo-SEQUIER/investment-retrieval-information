# AI Equity Discovery Agent

An AI-native research pipeline that scans **X/Twitter** and **Reddit** every day to discover interesting **AI-related public companies**, then enriches those ideas with factual company research such as:

- what the company does
- market cap **in USD**
- revenue **in USD**
- exchange / country
- sector / industry
- why the stock may be trending

This project is built as a **LangChain / Deep Agents** system for **discovery and research**, not for trade execution.

---

## Goal

The goal of this project is to build a daily agent that can:

1. read curated social sources on **X** and **Reddit**
2. identify public companies and tickers being discussed
3. focus on names relevant to the **AI ecosystem**
4. research each company on the open internet
5. rank the best ideas
6. generate a concise daily report / Telegram digest

This is meant to help surface **new stocks, new narratives, and new names to research**.

---

## Investment Focus

This is **not** a general stock screener.

The agent focuses primarily on **AI-related equities**, broadly defined across the AI value chain, including:

- hyperscalers / cloud platforms
- semiconductors
- AI accelerators / GPUs / custom chips
- memory and storage
- networking / interconnect
- optics / photonics
- datacenter infrastructure
- power / cooling
- energy linked to datacenter expansion
- foundries, packaging, and supporting industrial supply chains

Examples of themes the agent should pick up:

- hyperscaler capex
- GPU demand
- optical interconnect
- datacenter buildout
- energy demand from AI
- semiconductor bottlenecks
- advanced packaging
- memory upcycles

---

## What the Agent Does

### 1. Social discovery
The agent scans curated sources from:

- **X / Twitter**
- **Reddit**

It looks for:

- stock tickers
- company names
- repeated mentions
- unusual spikes in discussion
- new companies not seen before
- AI-related narratives and themes

### 2. Company enrichment
For each candidate company, the agent researches:

- official company identity
- what the company does
- market cap
- revenue
- country / exchange
- sector / industry
- why it matters to the AI ecosystem

### 3. Ranking and reporting
The agent ranks names based on:

- mention frequency
- source quality
- novelty
- cross-source confirmation
- AI relevance
- company-resolution confidence

Then it outputs a clean daily digest.

---

## What This Project Is Not

This project is **not**:

- a live trading bot
- a broker execution engine
- a portfolio manager
- a financial advisor
- a sentiment-only hype tracker

Social media is used for **discovery**, not as a source of truth.

All company facts should be verified through reputable public sources.

---

## Tech Stack

### Agent framework
- **LangChain**
- **LangGraph / Deep Agents**

Reason:
- good orchestration for multi-step workflows
- tool calling
- structured outputs
- agent + subagent style pipelines
- easier separation between discovery, enrichment, ranking, and reporting

### X / Twitter ingestion
- **twscrape**

Reason:
- practical open-source option for reading curated X accounts
- suitable for prototype / discovery workflows
- useful for extracting posts, timelines, and social signals

### Reddit ingestion
- **PRAW** or **asyncpraw**

Reason:
- official Reddit API access
- stable for subreddit-based ingestion
- better than fragile scraping for Reddit

### Web research / enrichment
- **httpx**
- **BeautifulSoup**
- **trafilatura** (for clean article/page extraction)
- optional search provider integration later if needed

### Data / storage
- **SQLite** for local persistence in v1
- possible upgrade later to **Postgres**

### Output
- daily markdown report
- terminal summary
- optional Telegram digest

---

## Planned Data Sources

### Social sources
The system starts from curated discovery inputs such as:

#### X / Twitter
Seed accounts like:
- `@jukan05`
- `@zephyr_z9`
- `@aleabitoreddit`

and more accounts discovered over time.

#### Reddit
Selected subreddits related to:
- stocks
- investing
- semiconductors
- AI
- datacenters
- energy / infrastructure
- growth / tech discussions

### Company research sources
The enrichment layer should prioritize:

- official company websites
- investor relations pages
- exchange listings
- reputable financial data pages
- reputable business news / reference sources

---

## Core Output Fields

For each company surfaced by the agent, the report should aim to include:

- company name
- ticker
- exchange
- country
- sector / industry
- short business description
- market cap **in USD**
- revenue **in USD**
- why it is relevant to the AI ecosystem
- why it appears to be trending
- confidence / caveat notes

### Currency rule
All key financial values shown to the user should be normalized to **USD**.

That includes:
- market cap
- revenue

---

## Example Daily Output

```text
AI EQUITY DISCOVERY — 2026-04-11

Top names:
1. Company A (TICKER)
   - Makes optical interconnect components for AI datacenters
   - Market cap: $8.2B
   - Revenue: $1.4B
   - Mentioned across X and Reddit
   - Trending due to AI network / optics narrative

2. Company B (TICKER)
   - Supplies power infrastructure to hyperscalers
   - Market cap: $15.7B
   - Revenue: $4.8B
   - Rising discussion tied to datacenter power demand

Themes:
- optical / photonics
- datacenter energy
- advanced packaging