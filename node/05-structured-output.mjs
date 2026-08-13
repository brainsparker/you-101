#!/usr/bin/env node
/**
 * Chapter 5: Schema in, JSON out.
 *
 * Add output_schema and output.content comes back as a typed JSON object
 * instead of Markdown (output.content_type becomes "object"; sources stay
 * in output.sources). Rules that matter:
 *   - every object needs properties AND additionalProperties: false
 *   - every property must be listed in required; make fields optional by
 *     adding "null" to their type, e.g. ["string", "null"]
 *   - not supported with lite effort (422); standard and up only
 *
 * This example fact-checks a claim into { verdict, summary, key_evidence }.
 *
 * Run:  node 05-structured-output.mjs "some claim to check"
 * Docs: https://you.com/docs/guides/research  (Structured Output)
 */
const key = process.env.YDC_API_KEY;
if (!key) {
  console.error(
    "Set YDC_API_KEY first. Get a key with $100 free credits: https://you.com/platform",
  );
  process.exit(1);
}

const claim =
  process.argv.slice(2).join(" ") ||
  "The majority of new AI agent frameworks released in 2026 ship with MCP support.";

const output_schema = {
  type: "object",
  properties: {
    verdict: { type: "string", enum: ["supported", "mixed", "unsupported"] },
    summary: { type: "string" },
    key_evidence: { type: "array", items: { type: "string" } },
  },
  required: ["verdict", "summary", "key_evidence"],
  additionalProperties: false,
};

console.error("Fact-checking (standard effort, ~10-30s)...");

const res = await fetch("https://api.you.com/v1/research", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({
    input: `Fact-check this claim: "${claim}"`,
    research_effort: "standard",
    output_schema,
  }),
});

if (!res.ok) {
  console.error(`HTTP ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const { output } = await res.json();

// content is a JSON object conforming to the schema, not a string.
console.log(JSON.stringify(output.content, null, 2));
console.log("\n--- sources ---");
output.sources.forEach((s, i) => console.log(`[${i + 1}] ${s.title ?? ""} ${s.url}`));
