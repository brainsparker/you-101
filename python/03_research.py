#!/usr/bin/env python3
"""Chapter 3: From results to answers.

POST /v1/research runs an agentic loop over Search, Contents, and Live
News, then synthesizes a Markdown answer with inline citations like
[[1]] that reference the sources array. One call, cited answer.

Effort levels: lite (<10s, $12/1k), standard (default, ~10-30s, $50/1k),
deep (<120s, $100/1k), exhaustive (<300s, $450/1k), frontier (background
only, $1200/1k).

Run:  python3 03_research.py "your question"
Docs: https://you.com/docs/guides/research
"""

import json
import os
import sys
import urllib.request

key = os.environ.get("YDC_API_KEY")
if not key:
    sys.exit(
        "Set YDC_API_KEY first. Get a key with $100 free credits: "
        "https://you.com/platform"
    )

question = " ".join(sys.argv[1:]) or (
    "Which web search APIs are AI agent builders adopting in 2026, and why?"
)

print("Researching (standard effort, ~10-30s)...", file=sys.stderr)

req = urllib.request.Request(
    "https://api.you.com/v1/research",
    data=json.dumps({"input": question, "research_effort": "standard"}).encode(),
    headers={"content-type": "application/json", "x-api-key": key},
    method="POST",
)

with urllib.request.urlopen(req, timeout=180) as res:
    data = json.load(res)

output = data["output"]
print(output["content"])
print("\n--- sources ---")
for i, source in enumerate(output["sources"], 1):
    print(f"[{i}] {source.get('title', '')} {source['url']}")
if data.get("warnings"):
    print("\nwarnings:", "; ".join(data["warnings"]))
