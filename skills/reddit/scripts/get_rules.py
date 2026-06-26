#!/usr/bin/env python3
"""Get subreddit rules to understand posting requirements."""

import argparse
import requests
import sys
import time
from toon_format import encode as toon_encode


def main():
    parser = argparse.ArgumentParser(
        description="Get subreddit rules before posting",
        epilog="Example: python3 scripts/get_rules.py ClaudeAI"
    )
    parser.add_argument("subreddit", help="Subreddit name (without r/)")
    args = parser.parse_args()

    headers = {"User-Agent": "python:reddit-skill:v1.0.0 (by /u/developer)"}
    url = f"https://www.reddit.com/r/{args.subreddit}/about/rules.json"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(1)
    except requests.exceptions.RequestException as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if response.status_code == 404:
        print(f"error: r/{args.subreddit} not found", file=sys.stderr)
        sys.exit(1)
    if response.status_code != 200:
        print(f"error: HTTP {response.status_code}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    rules = data.get("rules", [])

    if not rules:
        print(f"no_rules: true")
        return

    cleaned = [
        {
            "short_name": r.get("short_name", ""),
            "kind": r.get("kind", "all"),
            "description": (r.get("description") or "")[:200],
        }
        for r in rules
    ]
    print(f"rules for r/{args.subreddit}:")
    print(toon_encode(cleaned))


if __name__ == "__main__":
    main()
