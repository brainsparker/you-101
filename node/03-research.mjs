#!/usr/bin/env node
/**
 * Chapter 3: From results to answers.
 *
 * POST /v1/research runs an agentic loop over Search, Contents, and Live
 * News, then synthesizes a Markdown answer with inline citations like
 * [[1]] that reference the sources array. One call, cited answer.
 *
 * Effort levels: lite (<10s, $12/1k), standard (default, ~10-30s, $50/1k),
 * deep (<120s, $100/1k), exhaustive (<300s, $450/1k), frontier (background
 * only, $1200/1k).
 *
 * Run:  node 03-research.mjs "your question"
 * Docs: https://you.com/docs/guides/research
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
  "Which web search APIs are AI agent builders adopting in 2026, and why?";

console.error("Researching (standard effort, ~10-30s)...");

const res = await fetch("https://api.you.com/v1/research", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({ input, research_effort: "standard" }),
});

if (!res.ok) {
  console.error(`HTTP ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const { output, warnings } = await res.json();

console.log(output.content);
console.log("\n--- sources ---");
output.sources.forEach((s, i) => console.log(`[${i + 1}] ${s.title ?? ""} ${s.url}`));
if (warnings?.length) console.log(`\nwarnings: ${warnings.join("; ")}`);
