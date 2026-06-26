#!/usr/bin/env python3
"""
Get posts from a subreddit.
--sort best requires SCRAPECREATORS_API_KEY (not available via public API).
Usage: python3 scripts/get_posts.py python --sort hot --limit 20
       python3 scripts/get_posts.py ClaudeAI --sort best --limit 10
"""
import argparse
from toon_format import encode as toon_encode
from reddit_api import api_get, print_posts_list, print_pagination


def _get_best_posts(subreddit: str, limit: int, cursor: str):
    from scrapecreators_api import sc_get
    data = sc_get("/v1/reddit/subreddit", {"subreddit": subreddit, "sort": "best", "limit": limit, "cursor": cursor})
    posts = data.get("posts", [])
    print(f"r/{subreddit}/best:")
    print(toon_encode(posts))
    next_cursor = data.get("cursor")
    if next_cursor:
        print(toon_encode({"has_next_page": True, "next_cursor": next_cursor}))


def main():
    parser = argparse.ArgumentParser(description="Get subreddit posts")
    parser.add_argument("subreddit", help="Subreddit name (without r/)")
    parser.add_argument("--sort", "-s",
                        choices=["hot", "new", "top", "rising", "controversial", "best"],
                        default="hot", help="Sort method (default: hot); 'best' requires SCRAPECREATORS_API_KEY")
    parser.add_argument("--time", "-t", choices=["hour", "day", "week", "month", "year", "all"],
                        help="Time filter for top/controversial")
    parser.add_argument("--limit", "-l", type=int, default=25, help="Max posts (max 100)")
    parser.add_argument("--after", "-a", help="Pagination cursor")
    args = parser.parse_args()

    if args.sort == "best":
        _get_best_posts(args.subreddit, min(args.limit, 100), args.after)
        return

    path = f"r/{args.subreddit}/{args.sort}"
    params = {
        "limit": min(args.limit, 100),
        "after": args.after,
    }
    if args.time and args.sort in ["top", "controversial"]:
        params["t"] = args.time

    data = api_get(path, params)
    listing = data.get("data", {})
    posts = listing.get("children", [])

    label = f"r/{args.subreddit}/{args.sort}"
    if args.time:
        label += f"/{args.time}"
    print_posts_list(posts, label)
    print_pagination(listing)


if __name__ == "__main__":
    main()
