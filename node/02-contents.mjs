#!/usr/bin/env node
/**
 * Chapter 2 (legacy): Clean page content with the Contents API.
 *
 * POST /v1/contents fetches one or more URLs and returns clean content
 * (no nav, no ads). It still works, but the Extract API replaced it in
 * November 2026 and it will not get new features. New code should start
 * from 02-extract.mjs. This file stays for anyone maintaining an existing
 * Contents integration: up to 10 URLs per request, and the response is an
 * array of pages.
 *
 * Run:  node 02-contents.mjs https://you.com/docs [more urls...]
 * Docs: https://you.com/docs/api-reference/contents
 */
const key = process.env.YDC_API_KEY;
if (!key) {
  console.error(
    "Set YDC_API_KEY first. Get a key with $100 free credits: https://you.com/platform",
  );
  process.exit(1);
}

const urls = process.argv.slice(2);
if (urls.length === 0) {
  console.error("Usage: node 02-contents.mjs <url> [more urls...]");
  process.exit(1);
}

const res = await fetch("https://api.you.com/v1/contents", {
  method: "POST",
  headers: { "content-type": "application/json", "x-api-key": key },
  body: JSON.stringify({ urls }),
});

if (!res.ok) {
  console.error(`HTTP ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2).slice(0, 6000));
