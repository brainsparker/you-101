#!/usr/bin/env python3
"""Chapter 2: Read a page or a PDF.

POST /v1/extract fetches one webpage or PDF and returns it as clean
Markdown (or HTML): the "read this URL" primitive for RAG pipelines
and agents. PDF tables keep their rows and columns. It replaces the
Contents API (see 02_contents.py for the legacy call).

One URL per request, so a list of URLs means concurrent requests.
This script sends them all at once.

Run:  python3 02_extract.py https://you.com/docs [more urls...]
      python3 02_extract.py https://arxiv.org/pdf/2512.06710 --lite --timeout 60

Flags (each maps to one request field; with none set, the body is
just {"url": ...}):
  --html        full_page.extraction_formats: ["markdown", "html"]
  --fresh       extraction_source: "fetch"  (always crawl live)
  --cached      extraction_source: "cache"  (cache only, fastest)
  --lite        parse_effort: "lite"  (text PDFs, no per-page charge)
  --timeout N   timeout: N  (whole request, 2 to 100 seconds, default 30)

Docs: https://you.com/docs/api-reference/extract
"""

import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ENDPOINT = "https://ydc-index.io/v1/extract"

key = os.environ.get("YDC_API_KEY")
if not key:
    sys.exit(
        "Set YDC_API_KEY first. Get a key with $100 free credits: "
        "https://you.com/platform"
    )

USAGE = (
    "Usage: python3 02_extract.py <url> [more urls...] "
    "[--html] [--fresh | --cached] [--lite] [--timeout N]"
)

urls = []
options = {}
args = sys.argv[1:]
i = 0
while i < len(args):
    arg = args[i]
    if arg == "--html":
        options["full_page"] = {"extraction_formats": ["markdown", "html"]}
    elif arg in ("--fresh", "--cached"):
        if "extraction_source" in options:
            sys.exit("Pick one of --fresh and --cached.")
        options["extraction_source"] = "fetch" if arg == "--fresh" else "cache"
    elif arg == "--lite":
        options["parse_effort"] = "lite"
    elif arg == "--timeout":
        i += 1
        value = args[i] if i < len(args) else ""
        if not value.isdigit() or not 2 <= int(value) <= 100:
            sys.exit("--timeout takes a whole number of seconds from 2 to 100.")
        options["timeout"] = int(value)
    elif arg.startswith("--"):
        sys.exit(f"Unknown flag {arg}\n{USAGE}")
    else:
        urls.append(arg)
    i += 1
if not urls:
    sys.exit(USAGE)


def describe_error(status, text):
    """Turn an error response into one readable line.

    Extract errors carry a stable `code` and a `retryable` flag. Branch on
    those, never on the message. Some gateway responses (401, 403, and
    sometimes 402) use a flatter body, so read both shapes.
    """
    try:
        body = json.loads(text)
    except ValueError:
        return f"HTTP {status}: {text[:300]}"
    if not isinstance(body, dict):
        return f"HTTP {status}: {text[:300]}"
    error = body.get("error")
    nested = error if isinstance(error, dict) else {}
    code = nested.get("code") or (error if isinstance(error, str) else "")
    message = (
        nested.get("message") or body.get("message") or body.get("detail") or text[:300]
    )
    retry = ", retryable" if nested.get("retryable") is True else ""
    details = nested.get("details")
    reason = details.get("reason") if isinstance(details, dict) else None
    hint = ""
    if code in ("timeout", "pdf_too_large"):
        hint = " Raise --timeout (up to 100)."
    elif code == "payment_required" or status == 402:
        hint = " Add credits at https://you.com/platform."
    return (
        f"HTTP {status}{' ' + code if code else ''}{retry}: {message}"
        f"{' (' + reason + ')' if reason else ''}{hint}"
    )


def extract(url):
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"url": url, **options}).encode(),
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            # Some You.com hosts answer urllib's default User-Agent with a 403.
            "user-agent": "you-101",
        },
        method="POST",
    )
    # Give the socket a little longer than the API's own deadline, so a slow
    # page comes back as the API's 504 rather than a client-side timeout.
    try:
        with urllib.request.urlopen(req, timeout=options.get("timeout", 30) + 20) as res:
            return json.load(res)
    except urllib.error.HTTPError as err:
        raise RuntimeError(
            describe_error(err.code, err.read().decode("utf-8", "replace"))
        ) from None
    except (urllib.error.URLError, TimeoutError) as err:
        raise RuntimeError(f"Request failed: {getattr(err, 'reason', err)}") from None


def attempt(url):
    try:
        return extract(url), None
    except RuntimeError as err:
        return None, str(err)


with ThreadPoolExecutor(max_workers=min(8, len(urls))) as pool:
    outcomes = list(pool.map(attempt, urls))

failed = 0
for url, (page, error) in zip(urls, outcomes):
    print(f"\n=== {url} ===")
    if error:
        failed += 1
        print(error)
        continue
    # An empty object (or a missing `contents`) means nothing was extracted.
    # With --cached that is the normal answer for a page not in the cache.
    content = (page.get("contents") or {}).get("full_page")
    if not content:
        print("Nothing extracted (the response had no contents).")
        continue
    markdown = content.get("markdown") or ""
    html = content.get("html")
    print(f"title:   {page.get('title') or '(none)'}")
    print(f"source:  {page.get('extraction_source')}")
    print(
        f"length:  {len(markdown)} chars of markdown"
        + (f", {len(html)} chars of html" if html else "")
    )
    print(f"\n{markdown[:1500]}")
    if len(markdown) > 1500:
        print("\n[truncated for the terminal]")

sys.exit(1 if failed else 0)
