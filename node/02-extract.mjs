#!/usr/bin/env node
/**
 * Chapter 2: Read a page or a PDF.
 *
 * POST /v1/extract fetches one webpage or PDF and returns it as clean
 * Markdown (or HTML): the "read this URL" primitive for RAG pipelines
 * and agents. PDF tables keep their rows and columns. It replaces the
 * Contents API (see 02-contents.mjs for the legacy call).
 *
 * One URL per request, so a list of URLs means concurrent requests.
 * This script sends them all at once.
 *
 * Run:  node 02-extract.mjs https://you.com/docs [more urls...]
 *       node 02-extract.mjs https://arxiv.org/pdf/2512.06710 --lite --timeout 60
 *
 * Flags (each maps to one request field; with none set, the body is
 * just { url }):
 *   --html        full_page.extraction_formats: ["markdown", "html"]
 *   --fresh       extraction_source: "fetch"  (always crawl live)
 *   --cached      extraction_source: "cache"  (cache only, fastest)
 *   --lite        parse_effort: "lite"  (text PDFs, no per-page charge)
 *   --timeout N   timeout: N  (whole request, 2 to 100 seconds, default 30)
 *
 * Docs: https://you.com/docs/api-reference/extract
 */
const ENDPOINT = "https://ydc-index.io/v1/extract";

const key = process.env.YDC_API_KEY;
if (!key) {
  console.error(
    "Set YDC_API_KEY first. Get a key with $100 free credits: https://you.com/platform",
  );
  process.exit(1);
}

const USAGE =
  "Usage: node 02-extract.mjs <url> [more urls...] [--html] [--fresh | --cached] [--lite] [--timeout N]";

const urls = [];
const options = {};
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg === "--html") {
    options.full_page = { extraction_formats: ["markdown", "html"] };
  } else if (arg === "--fresh" || arg === "--cached") {
    if (options.extraction_source) {
      console.error("Pick one of --fresh and --cached.");
      process.exit(1);
    }
    options.extraction_source = arg === "--fresh" ? "fetch" : "cache";
  } else if (arg === "--lite") {
    options.parse_effort = "lite";
  } else if (arg === "--timeout") {
    const seconds = Number(args[++i]);
    if (!Number.isInteger(seconds) || seconds < 2 || seconds > 100) {
      console.error("--timeout takes a whole number of seconds from 2 to 100.");
      process.exit(1);
    }
    options.timeout = seconds;
  } else if (arg.startsWith("--")) {
    console.error(`Unknown flag ${arg}\n${USAGE}`);
    process.exit(1);
  } else {
    urls.push(arg);
  }
}
if (urls.length === 0) {
  console.error(USAGE);
  process.exit(1);
}

/**
 * Extract errors carry a stable `code` and a `retryable` flag. Branch on
 * those, never on the message. Some gateway responses (401, 403, and
 * sometimes 402) use a flatter body, so read both shapes.
 */
function describeError(status, text) {
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    return `HTTP ${status}: ${text.slice(0, 300)}`;
  }
  const nested = body.error && typeof body.error === "object" ? body.error : {};
  const code = nested.code ?? (typeof body.error === "string" ? body.error : "");
  const message = nested.message ?? body.message ?? body.detail ?? text.slice(0, 300);
  const retry = nested.retryable === true ? ", retryable" : "";
  const reason = nested.details?.reason ? ` (${nested.details.reason})` : "";
  let hint = "";
  if (code === "timeout" || code === "pdf_too_large") {
    hint = " Raise --timeout (up to 100).";
  } else if (code === "payment_required" || status === 402) {
    hint = " Add credits at https://you.com/platform.";
  }
  return `HTTP ${status}${code ? ` ${code}` : ""}${retry}: ${message}${reason}${hint}`;
}

async function extract(url) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "content-type": "application/json", "x-api-key": key },
    body: JSON.stringify({ url, ...options }),
  });
  if (!res.ok) throw new Error(describeError(res.status, await res.text()));
  return res.json();
}

const pages = await Promise.allSettled(urls.map(extract));

let failed = 0;
for (const [i, outcome] of pages.entries()) {
  console.log(`\n=== ${urls[i]} ===`);
  if (outcome.status === "rejected") {
    failed++;
    console.log(outcome.reason.message);
    continue;
  }
  const page = outcome.value;
  // An empty object (or a missing `contents`) means nothing was extracted.
  // With --cached that is the normal answer for a page not in the cache.
  const content = page.contents?.full_page;
  if (!content) {
    console.log("Nothing extracted (the response had no contents).");
    continue;
  }
  const markdown = content.markdown ?? "";
  console.log(`title:   ${page.title ?? "(none)"}`);
  console.log(`source:  ${page.extraction_source}`);
  console.log(
    `length:  ${markdown.length} chars of markdown` +
      (content.html ? `, ${content.html.length} chars of html` : ""),
  );
  console.log(`\n${markdown.slice(0, 1500)}`);
  if (markdown.length > 1500) console.log("\n[truncated for the terminal]");
}

process.exitCode = failed ? 1 : 0;
