#!/usr/bin/env node
/**
 * Chapter 1: Your first search.
 *
 * POST /v1/search returns raw, LLM-ready web results: URLs, titles, and
 * snippets you can feed into your own pipeline. This is the primitive;
 * later chapters build synthesis on top of it.
 *
 * Run:  node 01-search.mjs "your query"
 * Docs: https://you.com/docs/api-reference/search/v1-search
 */
const key = process.env.YDC_API_KEY;
if (!key) {
  console.error(
    "Set YDC_API_KEY first. Get a key with $100 free credits: https://you.com/platform",
  );
  process.exit(1);
}

const query =
  process.argv.slice(2).join(" ") || "latest developments in AI search APIs";

const res = await fetch("https://api.you.com/v1/search", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({ query }),
});

if (!res.ok) {
  console.error(`HTTP ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();

// Print the raw response (truncated) so you can see the exact shape,
// then build typed extraction for the fields your app needs.
console.log(JSON.stringify(data, null, 2).slice(0, 6000));
