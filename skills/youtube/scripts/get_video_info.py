#!/usr/bin/env python3
"""
Get video information by ID or URL
Usage: python3 scripts/get_video_info.py VIDEO_ID
"""
import argparse
import sys
from youtube_api import youtube_api, parse_video_id, format_duration, format_count


def main():
    parser = argparse.ArgumentParser(description="Get YouTube video info")
    parser.add_argument("video", help="Video ID or URL")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    video_id = parse_video_id(args.video)
    result = youtube_api("videos", {
        "part": "snippet,contentDetails,statistics",
        "id": video_id,
    })

    items = result.get("items", [])
    if not items:
        print(f"error: Video not found: {video_id}", file=sys.stderr)
        sys.exit(1)

    video = items[0]
    snippet = video.get("snippet", {})
    stats = video.get("statistics", {})
    content = video.get("contentDetails", {})

    if args.json:
        import json
        print(json.dumps(video, indent=2))
        return

    print(f"videoId: {video_id}")
    print(f"title: {snippet.get('title', '')}")
    print(f"channel: {snippet.get('channelTitle', '')} (id: {snippet.get('channelId', '')})")
    print(f"published: {snippet.get('publishedAt', '')[:10]}")
    print(f"duration: {format_duration(content.get('duration', ''))}")
    print(f"views: {format_count(stats.get('viewCount', 0))}")
    print(f"likes: {format_count(stats.get('likeCount', 0))}")
    print(f"comments: {format_count(stats.get('commentCount', 0))}")
    print(f"description: {snippet.get('description', '')[:200]}")
    
    tags = snippet.get("tags", [])[:5]
    if tags:
        print(f"tags: {', '.join(tags)}")


if __name__ == "__main__":
    main()
