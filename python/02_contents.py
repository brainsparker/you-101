#!/usr/bin/env python3
"""Chapter 2 (legacy): Clean page content with the Contents API.

POST /v1/contents fetches one or more URLs and returns clean content
(no nav, no ads). It still works, but the Extract API replaced it in
November 2026 and it will not get new features. New code should start
from 02_extract.py. This file stays for anyone maintaining an existing
Contents integration: up to 10 URLs per request, and the response is an
array of pages.

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
    headers={
        "content-type": "application/json",
        "x-api-key": key,
        # api.you.com answers urllib's default User-Agent with a 403.
        "user-agent": "you-101",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=120) as res:
    data = json.load(res)

print(json.dumps(data, indent=2)[:6000])
