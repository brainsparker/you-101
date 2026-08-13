#!/usr/bin/env python3
"""Chapter 2: Clean page content.

POST /v1/contents fetches one or more URLs and returns clean content
(no nav, no ads): the "read the page" primitive for RAG pipelines and
agents.

Run:  python3 02_contents.py https://you.com/docs [more urls...]
Docs: https://you.com/docs/api-reference/contents
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

urls = sys.argv[1:]
if not urls:
    sys.exit("Usage: python3 02_contents.py <url> [more urls...]")

req = urllib.request.Request(
    "https://api.you.com/v1/contents",
    data=json.dumps({"urls": urls}).encode(),
    headers={"content-type": "application/json", "x-api-key": key},
    method="POST",
)

with urllib.request.urlopen(req, timeout=120) as res:
    data = json.load(res)

print(json.dumps(data, indent=2)[:6000])
