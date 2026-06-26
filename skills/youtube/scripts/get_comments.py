#!/usr/bin/env python3
"""
Get video comments
Usage: python3 scripts/get_comments.py VIDEO_ID --limit 50
"""
import argparse
import sys
from youtube_api import youtube_api, parse_video_id, format_count


def main():
    parser = argparse.ArgumentParser(description="Get YouTube video comments")
    parser.add_argument("video", help="Video ID or URL")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--sort", "-s", choices=["relevance", "time"], default="relevance",
                        help="Sort order (default: relevance)")
    args = parser.parse_args()

    video_id = parse_video_id(args.video)
    result = youtube_api("commentThreads", {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": min(args.limit, 100),
        "order": args.sort,
        "textFormat": "plainText",
    })

    items = result.get("items", [])
    total = result.get("pageInfo", {}).get("totalResults", 0)

    print(f"videoId: {video_id}")
    print(f"total: {total}")
    print(f"sort: {args.sort}")
    print(f"comments[{len(items)}]{{author,text,likes,replies}}:")

    for item in items:
        snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
        author = snippet.get("authorDisplayName", "")
        text = snippet.get("textDisplay", "").replace("\n", " ")[:100]
        likes = snippet.get("likeCount", 0)
        replies = item.get("snippet", {}).get("totalReplyCount", 0)
        print(f"  {author}: {text} ({format_count(likes)} likes, {replies} replies)")


if __name__ == "__main__":
    main()
