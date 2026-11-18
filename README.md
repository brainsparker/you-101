# you-101

Learn the You.com API in seven small, runnable scripts: search the live web, read pages and PDFs, get cited research answers, run minutes-long research without long requests, get typed JSON back, use the finance index, and scope research to specific sites.

Every script is zero-dependency (Node 20+ built-in `fetch`, Python 3 stdlib `urllib`), self-contained, and safe to copy into your own project. For production use, reach for the official SDKs: [youdotcom-typescript-sdk](https://github.com/youdotcom-oss/youdotcom-typescript-sdk) and [youdotcom-python-sdk](https://github.com/youdotcom-oss/youdotcom-python-sdk).

## Setup (30 seconds)

1. Get an API key at [you.com/platform](https://you.com/platform). New accounts include $100 in credits.
2. Export it:

```bash
export YDC_API_KEY="your key"
```

Every endpoint authenticates with an `X-API-Key` header. The chapters call `https://api.you.com`, except chapter 2: the Extract API is documented on `https://ydc-index.io`. That's the whole setup.

Prefer trying before signing up? The MCP server has a free tier: point any MCP client at `https://api.you.com/mcp/free` for search (`you-search`) and page or PDF extraction (`you-extract`), no account needed.

## The chapters

| # | Run it | What you learn |
| --- | --- | --- |
| 1 | `node node/01-search.mjs "your query"` | `POST /v1/search`: raw, LLM-ready web results, the primitive under everything else |
| 2 | `node node/02-extract.mjs https://you.com/docs` | `POST /v1/extract`: one webpage or PDF as clean Markdown or HTML, with cache control, a request timeout, and PDF parse effort |
| 3 | `node node/03-research.mjs "your question"` | `POST /v1/research`: one call, a Markdown answer with `[[n]]` citations bound to a sources array |
| 4 | `node node/04-research-background.mjs "big question"` | `background: true`: task handle now, poll `GET /v1/research/{task_id}` for the result. Long research without long requests |
| 5 | `node node/05-structured-output.mjs "a claim"` | `output_schema`: typed JSON out instead of Markdown. The example is a mini fact-checker |
| 6 | `node node/06-finance-research.mjs "NVDA's latest quarter?"` | `POST /v1/finance_research`: the finance-optimized index (filings, fundamentals, analyst coverage) |
| 7 | `node node/07-site-scoped-research.mjs stripe.com "US card fees?"` | `source_control.include_domains`: site Q&A with zero RAG infrastructure |

Every chapter has a Python twin in `python/` (for example `python3 python/03_research.py "your question"`).

Chapter 2 used to teach the Contents API. That script is still here as `node/02-contents.mjs` (and `python/02_contents.py`) for existing integrations; the migration table is under "Extract replaces Contents" below.

## Concepts that carry across chapters

**Effort is the main dial.** `research_effort` trades latency and cost for depth:

| Level | Latency | Price per 1k | Notes |
| --- | --- | --- | --- |
| `lite` | <10s | $12 | No `output_schema` support |
| `standard` | ~10-30s | $50 | The default |
| `deep` | <120s | $100 | Use background mode when hosting |
| `exhaustive` | <300s | $450 | Dozens of sources |
| `frontier` | 30s to hours | $1,200 | Background mode required |

**Citations are load-bearing.** Research answers arrive as Markdown with `[[1]]` or grouped `[[1, 2]]` markers that index into `output.sources` (url, title, snippets). Render them as links; they are the receipts.

**Background mode is the timeout answer.** Chapter 4's submit-then-poll loop is exactly how you run deep research behind serverless platforms that cap request duration (many cap at 20-30 seconds). There is also an SSE stream per task (`GET /v1/research/{task_id}/stream`) with `?from_id=N` replay for lossless reconnects.

**Schema rules for structured output.** Root must be an object; every object needs `properties` and `additionalProperties: false`; every property goes in `required` (make fields optional by adding `"null"` to their type). Not supported with `lite`.

**Extract is one URL in, one page out.** `POST /v1/extract` takes a single `url` (webpage or PDF) and returns one object with the page in `contents.full_page.markdown`. Three dials matter:

| Field | Values | What it changes |
| --- | --- | --- |
| `extraction_source` | `blend` (default), `cache`, `fetch` | Cache when available, cache only (fastest), or always crawl live (freshest) |
| `timeout` | 2 to 100 seconds, default 30 | Caps the whole request; past it you get a `504` with code `timeout` |
| `parse_effort` | `standard` (default), `lite` | PDFs only. `standard` also reads charts and images and bills per page; `lite` reads embedded text with no page charge |

Pricing is $0.90 per 1,000 URLs, plus $0.50 per 1,000 PDF pages at `standard`. Two habits to copy from the chapter: check for `contents` before reading it (an empty object means nothing was extracted), and branch on the error's stable `code` and `retryable` flag, not its message. To read a list of URLs, send the requests concurrently.

**Extract replaces Contents.** The Contents API (`POST /v1/contents`) still works but gets no new features. Moving a call over:

| Contents API | Extract API |
| --- | --- |
| `urls`, up to 10 per request | `url`, one per request (send several concurrently) |
| `formats: ["markdown", "html"]` | `full_page.extraction_formats: ["markdown", "html"]` |
| `crawl_timeout` (per URL) | `timeout` (whole request). Sending `crawl_timeout` is a `422` |
| `max_age` | `extraction_source`: `fetch` to skip the cache, `cache` to read only from it |
| Response is an array; read `page.markdown` | Response is one object; read `contents.full_page.markdown` |

**The finance endpoint is its own contract.** `POST /v1/finance_research` (underscore) takes only `input` and `research_effort` (`deep` or `exhaustive`), runs synchronously, and searches a financial index instead of the open web. No background mode, no `output_schema`, no `source_control`.

## Where to go next

Working apps, each one an MIT-licensed repo built on these exact patterns:

- [you-chat](https://github.com/brainsparker/you-chat): chapter 3 as a streaming chat UI
- [you-deep-research](https://github.com/brainsparker/you-deep-research): chapter 4 with live SSE progress and reconnects
- [you-company-researcher](https://github.com/brainsparker/you-company-researcher): chapter 5 as a typed company dossier
- [you-sheets](https://github.com/brainsparker/you-sheets): chapter 3 at `lite` effort, one call per spreadsheet cell
- [you-market-researcher](https://github.com/brainsparker/you-market-researcher): chapter 6 as portfolio briefs
- [you-site-research](https://github.com/brainsparker/you-site-research): chapter 7 as a full site Q&A app
- [you-meeting-prep](https://github.com/brainsparker/you-meeting-prep): chapters 3 and 4 as meeting prep sheets
- [you-fact-checker](https://github.com/brainsparker/you-fact-checker): chapter 5's mini fact-checker as a full app with a six-level verdict enum
- [you-news-brief](https://github.com/brainsparker/you-news-brief): freshness-scoped briefings built to run on a schedule
- [you-app-template](https://github.com/brainsparker/you-app-template): the starter they all began from

And for agents: every one of these APIs is exposed as MCP tools at `https://api.you.com/mcp`. See the [MCP guide](https://you.com/docs/build-with-agents/mcp-server).

## License

MIT. See [LICENSE](./LICENSE).
