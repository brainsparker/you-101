#!/usr/bin/env python3
"""Chapter 4: Long research without long requests.

Deep research can run for minutes, which fights client timeouts and
serverless request ceilings. Background mode fixes it: submit with
background=true, get a task handle instantly, then poll
GET /v1/research/{task_id} (or stream SSE from /stream) for the result.
A task moves through queued -> running -> completed | failed | cancelled.

Run:  python3 04_research_background.py "your question"
Docs: https://you.com/docs/guides/research  (Background Mode)
"""

import json
import os
import sys
import time
import urllib.request

key = os.environ.get("YDC_API_KEY")
if not key:
    sys.exit(
        "Set YDC_API_KEY first. Get a key with $100 free credits: "
        "https://you.com/platform"
    )

question = " ".join(sys.argv[1:]) or (
    "Map the competitive landscape of web search APIs for AI agents in 2026."
)

# 1. Submit. The response is a task handle, not the answer.
submit = urllib.request.Request(
    "https://api.you.com/v1/research",
    data=json.dumps(
        {"input": question, "research_effort": "deep", "background": True}
    ).encode(),
    headers={
        "content-type": "application/json",
        "x-api-key": key,
        # api.you.com answers urllib's default User-Agent with a 403.
        "user-agent": "you-101",
    },
    method="POST",
)
with urllib.request.urlopen(submit, timeout=60) as res:
    task = json.load(res)

print(f"Task {task['task_id']} submitted (status: {task['status']}).", file=sys.stderr)

# 2. Poll until the task reaches a terminal status.
started = time.time()
while True:
    time.sleep(3)
    poll = urllib.request.Request(
        f"https://api.you.com/v1/research/{task['task_id']}",
        headers={
            "x-api-key": key,
            # api.you.com answers urllib's default User-Agent with a 403.
            "user-agent": "you-101",
        },
    )
    with urllib.request.urlopen(poll, timeout=60) as res:
        detail = json.load(res)

    print(f"  {time.time() - started:.0f}s: {detail['status']}", file=sys.stderr)

    if detail["status"] == "completed" and detail["result"]:
        output = detail["result"]["output"]
        print(output["content"])
        print("\n--- sources ---")
        for i, source in enumerate(output["sources"], 1):
            print(f"[{i}] {source.get('title', '')} {source['url']}")
        break

    if detail["status"] in ("failed", "cancelled"):
        sys.exit(f"Task {detail['status']}: {detail.get('error') or 'no diagnostic'}")
