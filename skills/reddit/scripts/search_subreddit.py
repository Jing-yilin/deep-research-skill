#!/usr/bin/env python3
"""
Search within a subreddit (ScrapeCreators).
Returns separate posts, comments, and media arrays with cursor pagination.
Usage: python3 scripts/search_subreddit.py ClaudeAI "MCP server"
       python3 scripts/search_subreddit.py ClaudeAI "MCP server" --type all
"""
import argparse
from toon_format import encode as toon_encode
from scrapecreators_api import sc_get


def main():
    parser = argparse.ArgumentParser(description="Search within a subreddit (ScrapeCreators)")
    parser.add_argument("subreddit", help="Subreddit name (case-sensitive)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--type", choices=["posts", "comments", "media", "all"],
                        default="posts", help="Result type (default: posts)")
    parser.add_argument("--cursor", help="Pagination cursor from previous response")
    args = parser.parse_args()

    data = sc_get("/v1/reddit/subreddit/search", {
        "subreddit": args.subreddit,
        "query": args.query,
        "cursor": args.cursor,
    })

    print(f"query: {args.query} in r/{args.subreddit}")

    if args.type in ("posts", "all"):
        posts = data.get("posts", [])
        print(f"\nposts:")
        print(toon_encode(posts) if posts else "  (none)")

    if args.type in ("comments", "all"):
        comments = data.get("comments", [])
        print(f"\ncomments:")
        print(toon_encode(comments) if comments else "  (none)")

    if args.type in ("media", "all"):
        media = data.get("media", [])
        print(f"\nmedia:")
        print(toon_encode(media) if media else "  (none)")

    cursor = data.get("cursor")
    if cursor:
        print(toon_encode({"has_next_page": True, "next_cursor": cursor}))


if __name__ == "__main__":
    main()
