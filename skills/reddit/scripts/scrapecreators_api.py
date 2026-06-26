#!/usr/bin/env python3
"""
ScrapeCreators Reddit API helper.
Requires SCRAPECREATORS_API_KEY env var.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.scrapecreators.com"


def sc_get(path: str, params: dict = None) -> dict:
    api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        print("error: SCRAPECREATORS_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    url = f"{BASE_URL}{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)

    req = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"error: HTTP {e.code} — {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
