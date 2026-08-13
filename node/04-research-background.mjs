#!/usr/bin/env node
/**
 * Chapter 4: Long research without long requests.
 *
 * Deep research can run for minutes, which fights client timeouts and
 * serverless request ceilings. Background mode fixes it: submit with
 * background: true, get a task handle instantly, then poll
 * GET /v1/research/{task_id} (or stream SSE from /stream) for the result.
 * A task moves through queued -> running -> completed | failed | cancelled.
 *
 * Run:  node 04-research-background.mjs "your question"
 * Docs: https://you.com/docs/guides/research  (Background Mode)
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
  "Map the competitive landscape of web search APIs for AI agents in 2026.";

// 1. Submit. The response is a task handle, not the answer.
const submit = await fetch("https://api.you.com/v1/research", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({ input, research_effort: "deep", background: true }),
});
if (!submit.ok) {
  console.error(`HTTP ${submit.status}: ${await submit.text()}`);
  process.exit(1);
}
const task = await submit.json();
console.error(`Task ${task.task_id} submitted (status: ${task.status}).`);

// 2. Poll until the task reaches a terminal status.
const started = Date.now();
for (;;) {
  await new Promise((r) => setTimeout(r, 3000));
  const res = await fetch(`https://api.you.com/v1/research/${task.task_id}`, {
    headers: { "x-api-key": key },
  });
  if (!res.ok) {
    console.error(`HTTP ${res.status}: ${await res.text()}`);
    process.exit(1);
  }
  const detail = await res.json();
  const elapsed = ((Date.now() - started) / 1000).toFixed(0);
  console.error(`  ${elapsed}s: ${detail.status}`);

  if (detail.status === "completed" && detail.result) {
    console.log(detail.result.output.content);
    console.log("\n--- sources ---");
    detail.result.output.sources.forEach((s, i) =>
      console.log(`[${i + 1}] ${s.title ?? ""} ${s.url}`),
    );
    break;
  }
  if (detail.status === "failed" || detail.status === "cancelled") {
    console.error(`Task ${detail.status}: ${detail.error ?? "no diagnostic"}`);
    process.exit(1);
  }
}
