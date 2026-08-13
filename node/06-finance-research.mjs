#!/usr/bin/env node
/**
 * Chapter 6: The finance index.
 *
 * POST /v1/finance_research (note the underscore) is the Research API
 * pointed at a finance-optimized index: structured fundamentals, prices
 * across 42 exchanges, SEC filings, analyst coverage, and financial news.
 *
 * Contract differences from /v1/research:
 *   - parameters are input and research_effort ONLY
 *   - research_effort is deep (default, <120s) or exhaustive (<300s)
 *   - no background mode, no output_schema, no source_control
 *   - synchronous: expect this call to take a minute or more
 *
 * Run:  node 06-finance-research.mjs "What drove NVDA's latest quarter?"
 * Docs: https://you.com/docs/guides/finance-research
 */
const key = process.env.YDC_API_KEY;
if (!key) {
  console.error(
    "Set YDC_API_KEY first. Get a key with $100 free credits: https://you.com/platform",
  );
  process.exit(1);
}

const input =
  process.argv.slice(2).join(" ") ||
  "What drove NVIDIA's revenue growth in its most recent fiscal year?";

console.error("Finance research (deep effort, can take ~1-2 minutes)...");

const res = await fetch("https://api.you.com/v1/finance_research", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({ input, research_effort: "deep" }),
});

if (!res.ok) {
  console.error(`HTTP ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const { output } = await res.json();

console.log(output.content);
console.log("\n--- sources ---");
output.sources.forEach((s, i) => console.log(`[${i + 1}] ${s.title ?? ""} ${s.url}`));
