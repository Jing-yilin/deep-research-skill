#!/usr/bin/env python3
"""
Get channel information
Usage: python3 scripts/get_channel_info.py CHANNEL_ID
"""
import argparse
import sys
from youtube_api import youtube_api, format_count


def main():
    parser = argparse.ArgumentParser(description="Get YouTube channel info")
    parser.add_argument("channel", nargs="?", help="Channel ID")
    parser.add_argument("--username", "-u", help="Channel username (handle)")
    args = parser.parse_args()

    params = {"part": "snippet,statistics,contentDetails"}
    
    if args.username:
        # Try forUsername first, then forHandle
        handle = args.username.lstrip("@")
        params["forHandle"] = handle
    elif args.channel:
        params["id"] = args.channel
    else:
        print("error: Provide channel ID or --username", file=sys.stderr)
        sys.exit(1)

    result = youtube_api("channels", params)
    items = result.get("items", [])
    
    if not items:
        print("error: Channel not found", file=sys.stderr)
        sys.exit(1)

    channel = items[0]
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})

    print(f"channelId: {channel.get('id', '')}")
    print(f"title: {snippet.get('title', '')}")
    print(f"customUrl: {snippet.get('customUrl', '')}")
    print(f"subscribers: {format_count(stats.get('subscriberCount', 0))}")
    print(f"videos: {format_count(stats.get('videoCount', 0))}")
    print(f"views: {format_count(stats.get('viewCount', 0))}")
    print(f"description: {snippet.get('description', '')[:200]}")


if __name__ == "__main__":
    main()
