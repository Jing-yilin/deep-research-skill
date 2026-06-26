#!/usr/bin/env python3
"""
Search posts on Reddit.
--sort comment_count uses ScrapeCreators (requires SCRAPECREATORS_API_KEY).
Usage: python3 scripts/search_posts.py "AI agent" --subreddit ClaudeAI --limit 20
       python3 scripts/search_posts.py "Claude Code" --sort comment_count --trim
"""
import argparse
from toon_format import encode as toon_encode
from reddit_api import api_get, print_posts_list, print_pagination


def _search_sc(query: str, sort: str, limit: int, after: str, trim: bool):
    from scrapecreators_api import sc_get
    data = sc_get("/v1/reddit/search", {
        "query": query,
        "sort": sort,
        "limit": limit,
        "after": after,
        "trim": "true" if trim else None,
    })
    posts = data.get("posts", data.get("children", []))
    print(f"query: {query} (sort: {sort})")
    print(toon_encode(posts))
    next_cursor = data.get("after") or data.get("cursor")
    if next_cursor:
        print(toon_encode({"has_next_page": True, "next_cursor": next_cursor}))


def main():
    parser = argparse.ArgumentParser(description="Search Reddit posts")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--subreddit", "-r", help="Limit to subreddit")
    parser.add_argument("--sort", "-s",
                        choices=["relevance", "hot", "top", "new", "comments", "comment_count"],
                        default="relevance",
                        help="Sort method; 'comment_count' requires SCRAPECREATORS_API_KEY")
    parser.add_argument("--time", "-t", choices=["hour", "day", "week", "month", "year", "all"],
                        default="all", help="Time filter")
    parser.add_argument("--limit", "-l", type=int, default=25, help="Max posts")
    parser.add_argument("--after", "-a", help="Pagination cursor")
    parser.add_argument("--trim", action="store_true", help="Reduce response size (ScrapeCreators only)")
    args = parser.parse_args()

    if args.sort == "comment_count":
        _search_sc(args.query, "comment_count", min(args.limit, 100), args.after, args.trim)
        return

    if args.subreddit:
        path = f"r/{args.subreddit}/search"
        params = {
            "q": args.query,
            "restrict_sr": "1",
            "sort": args.sort,
            "t": args.time,
            "limit": min(args.limit, 100),
            "after": args.after,
        }
    else:
        path = "search"
        params = {
            "q": args.query,
            "sort": args.sort,
            "t": args.time,
            "limit": min(args.limit, 100),
            "after": args.after,
        }

    data = api_get(path, params)
    listing = data.get("data", {})
    posts = listing.get("children", [])

    label = f"search({args.query})"
    if args.subreddit:
        label = f"r/{args.subreddit}/search({args.query})"
    print(f"query: {args.query}")
    print(f"sort: {args.sort}, time: {args.time}")
    print_posts_list(posts, label)
    print_pagination(listing)


if __name__ == "__main__":
    main()
