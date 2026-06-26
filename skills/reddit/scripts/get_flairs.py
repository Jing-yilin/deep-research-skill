#!/usr/bin/env python3
"""Get available post flairs from a subreddit."""

import argparse
import requests
import sys
import time
from toon_format import encode as toon_encode


def main():
    parser = argparse.ArgumentParser(description="Get available post flairs from a subreddit")
    parser.add_argument("subreddit", help="Subreddit name (without r/)")
    args = parser.parse_args()

    headers = {"User-Agent": "python:reddit-skill:v1.0.0 (by /u/developer)"}
    url = f"https://www.reddit.com/r/{args.subreddit}/hot.json?limit=50"

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
    flairs = {}
    for post in data["data"]["children"]:
        pd = post["data"]
        if pd.get("link_flair_text"):
            flairs[pd["link_flair_text"]] = pd.get("link_flair_template_id", "")

    if not flairs:
        print(f"no_flairs: true")
        return

    cleaned = [{"flair": text, "id": fid} for text, fid in sorted(flairs.items())]
    print(f"flairs for r/{args.subreddit}:")
    print(toon_encode(cleaned))


if __name__ == "__main__":
    main()
