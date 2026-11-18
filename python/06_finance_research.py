#!/usr/bin/env python3
"""Chapter 6: The finance index.

POST /v1/finance_research (note the underscore) is the Research API
pointed at a finance-optimized index: structured fundamentals, prices
across 42 exchanges, SEC filings, analyst coverage, and financial news.

Contract differences from /v1/research:
  - parameters are input and research_effort ONLY
  - research_effort is deep (default, <120s) or exhaustive (<300s)
  - no background mode, no output_schema, no source_control
  - synchronous: expect this call to take a minute or more

Run:  python3 06_finance_research.py "What drove NVDA's latest quarter?"
Docs: https://you.com/docs/guides/finance-research
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
    "What drove NVIDIA's revenue growth in its most recent fiscal year?"
)

print("Finance research (deep effort, can take ~1-2 minutes)...", file=sys.stderr)

req = urllib.request.Request(
    "https://api.you.com/v1/finance_research",
    data=json.dumps({"input": question, "research_effort": "deep"}).encode(),
    headers={
        "content-type": "application/json",
        "x-api-key": key,
        # api.you.com answers urllib's default User-Agent with a 403.
        "user-agent": "you-101",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=360) as res:
    data = json.load(res)

output = data["output"]
print(output["content"])
print("\n--- sources ---")
for i, source in enumerate(output["sources"], 1):
    print(f"[{i}] {source.get('title', '')} {source['url']}")
