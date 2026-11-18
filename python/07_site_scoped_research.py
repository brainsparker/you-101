#!/usr/bin/env python3
"""Chapter 7: Scope research to specific sites.

source_control constrains which domains the research agent may search
and read. include_domains means "only these sites": instant site Q&A
with zero RAG infrastructure. Also available: exclude_domains,
boost_domains, freshness (day|week|month|year|YYYY-MM-DDtoYYYY-MM-DD),
and country. include_domains cannot combine with exclude/boost.

Run:  python3 07_site_scoped_research.py stripe.com "What are Stripe's US card fees?"
Docs: https://you.com/docs/guides/research  (Source Control)
"""

import json
import os
import sys
import urllib.parse
import urllib.request

key = os.environ.get("YDC_API_KEY")
if not key:
    sys.exit(
        "Set YDC_API_KEY first. Get a key with $100 free credits: "
        "https://you.com/platform"
    )

if len(sys.argv) < 3:
    sys.exit('Usage: python3 07_site_scoped_research.py <domain> "your question"')

domain = sys.argv[1]
question = " ".join(sys.argv[2:])

print(f"Researching within {domain} (standard effort)...", file=sys.stderr)

req = urllib.request.Request(
    "https://api.you.com/v1/research",
    data=json.dumps(
        {
            "input": question,
            "research_effort": "standard",
            "source_control": {"include_domains": [domain]},
        }
    ).encode(),
    headers={
        "content-type": "application/json",
        "x-api-key": key,
        # api.you.com answers urllib's default User-Agent with a 403.
        "user-agent": "you-101",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=180) as res:
    data = json.load(res)

output = data["output"]
print(output["content"])
print("\n--- pages consulted ---")
for i, source in enumerate(output["sources"], 1):
    host = urllib.parse.urlparse(source["url"]).hostname or ""
    on_scope = host == domain or host.endswith("." + domain)
    print(f"[{i}] {'on-scope ' if on_scope else 'OFF-SCOPE'} {source['url']}")
