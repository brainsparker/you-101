#!/usr/bin/env node
/**
 * Chapter 7: Scope research to specific sites.
 *
 * source_control constrains which domains the research agent may search
 * and read. include_domains means "only these sites": instant site Q&A
 * with zero RAG infrastructure. Also available: exclude_domains,
 * boost_domains, freshness (day|week|month|year|YYYY-MM-DDtoYYYY-MM-DD),
 * and country. include_domains cannot combine with exclude/boost.
 *
 * Run:  node 07-site-scoped-research.mjs stripe.com "What are Stripe's US card fees?"
 * Docs: https://you.com/docs/guides/research  (Source Control)
 */
const key = process.env.YDC_API_KEY;
if (!key) {
  console.error(
    "Set YDC_API_KEY first. Get a key with $100 free credits: https://you.com/platform",
  );
  process.exit(1);
}

const [domain, ...rest] = process.argv.slice(2);
const input = rest.join(" ");
if (!domain || !input) {
  console.error(
    'Usage: node 07-site-scoped-research.mjs <domain> "your question"',
  );
  process.exit(1);
}

console.error(`Researching within ${domain} (standard effort)...`);

const res = await fetch("https://api.you.com/v1/research", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({
    input,
    research_effort: "standard",
    source_control: { include_domains: [domain] },
  }),
});

if (!res.ok) {
  console.error(`HTTP ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const { output } = await res.json();

console.log(output.content);
console.log("\n--- pages consulted ---");
for (const [i, s] of output.sources.entries()) {
  const host = new URL(s.url).hostname;
  const onScope = host === domain || host.endsWith(`.${domain}`);
  console.log(`[${i + 1}] ${onScope ? "on-scope " : "OFF-SCOPE"} ${s.url}`);
}
