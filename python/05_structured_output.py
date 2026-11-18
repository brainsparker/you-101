#!/usr/bin/env python3
"""Chapter 5: Schema in, JSON out.

Add output_schema and output.content comes back as a typed JSON object
instead of Markdown (output.content_type becomes "object"; sources stay
in output.sources). Rules that matter:
  - every object needs properties AND additionalProperties: false
  - every property must be listed in required; make fields optional by
    adding "null" to their type, e.g. ["string", "null"]
  - not supported with lite effort (422); standard and up only

This example fact-checks a claim into {verdict, summary, key_evidence}.

Run:  python3 05_structured_output.py "some claim to check"
Docs: https://you.com/docs/guides/research  (Structured Output)
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

claim = " ".join(sys.argv[1:]) or (
    "The majority of new AI agent frameworks released in 2026 ship with MCP support."
)

output_schema = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "mixed", "unsupported"]},
        "summary": {"type": "string"},
        "key_evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["verdict", "summary", "key_evidence"],
    "additionalProperties": False,
}

print("Fact-checking (standard effort, ~10-30s)...", file=sys.stderr)

req = urllib.request.Request(
    "https://api.you.com/v1/research",
    data=json.dumps(
        {
            "input": f'Fact-check this claim: "{claim}"',
            "research_effort": "standard",
            "output_schema": output_schema,
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

# content is a JSON object conforming to the schema, not a string.
print(json.dumps(output["content"], indent=2))
print("\n--- sources ---")
for i, source in enumerate(output["sources"], 1):
    print(f"[{i}] {source.get('title', '')} {source['url']}")
