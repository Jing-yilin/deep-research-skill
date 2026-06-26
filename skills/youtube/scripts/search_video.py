#!/usr/bin/env python3
"""
Search videos on YouTube
Usage: python3 scripts/search_video.py "keyword" --limit 10
"""
import argparse
import sys
from youtube_api import youtube_api, format_count


def main():
    parser = argparse.ArgumentParser(description="Search YouTube videos")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results (default: 10)")
    args = parser.parse_args()

    result = youtube_api("search", {
        "part": "snippet",
        "q": args.query,
        "type": "video",
        "maxResults": args.limit,
    })

    items = result.get("items", [])
    total = result.get("pageInfo", {}).get("totalResults", 0)

    print(f"query: {args.query}")
    print(f"total: {total}")
    print(f"videos[{len(items)}]{{videoId,title,channel,published}}:")

    for item in items:
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId", "")
        title = snippet.get("title", "").replace(",", "，")[:60]
        channel = snippet.get("channelTitle", "")
        published = snippet.get("publishedAt", "")[:10]
        print(f"  {video_id},{title},{channel},{published}")


if __name__ == "__main__":
    main()
