#!/usr/bin/env python3
"""Chapter 1: Your first search.

POST /v1/search returns raw, LLM-ready web results: URLs, titles, and
snippets you can feed into your own pipeline. This is the primitive;
later chapters build synthesis on top of it.

Run:  python3 01_search.py "your query"
Docs: https://you.com/docs/api-reference/search/v1-search
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

query = " ".join(sys.argv[1:]) or "latest developments in AI search APIs"

req = urllib.request.Request(
    "https://api.you.com/v1/search",
    data=json.dumps({"query": query}).encode(),
    headers={
        "content-type": "application/json",
        "x-api-key": key,
        # api.you.com answers urllib's default User-Agent with a 403.
        "user-agent": "you-101",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=60) as res:
    data = json.load(res)

# Print the raw response (truncated) so you can see the exact shape,
# then build typed extraction for the fields your app needs.
print(json.dumps(data, indent=2)[:6000])
