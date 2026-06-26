#!/usr/bin/env python3
"""
Get post comments by URL via ScrapeCreators.
Supports cursor pagination and nested reply threading.
Usage: python3 scripts/get_post_comments_url.py "https://www.reddit.com/r/ClaudeAI/comments/abc123/title/"
"""
import argparse
from toon_format import encode as toon_encode
from scrapecreators_api import sc_get


def main():
    parser = argparse.ArgumentParser(description="Get post comments by URL (ScrapeCreators)")
    parser.add_argument("url", help="Full Reddit post URL")
    parser.add_argument("--cursor", help="Pagination cursor from previous response")
    args = parser.parse_args()

    data = sc_get("/v1/reddit/post/comments", {"url": args.url, "cursor": args.cursor})
    print(toon_encode(data))


if __name__ == "__main__":
    main()
