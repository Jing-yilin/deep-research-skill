#!/usr/bin/env python3
"""
Get playlist videos
Usage: python3 scripts/get_playlist.py PLAYLIST_ID --limit 50
"""
import argparse
import sys
from youtube_api import youtube_api, format_count


def main():
    parser = argparse.ArgumentParser(description="Get YouTube playlist videos")
    parser.add_argument("playlist_id", help="Playlist ID")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--info", "-i", action="store_true", help="Include playlist info")
    args = parser.parse_args()

    if args.info:
        info = youtube_api("playlists", {
            "part": "snippet,contentDetails",
            "id": args.playlist_id,
        })
        items = info.get("items", [])
        if items:
            snippet = items[0].get("snippet", {})
            details = items[0].get("contentDetails", {})
            print(f"playlistId: {args.playlist_id}")
            print(f"title: {snippet.get('title', '')}")
            print(f"channel: {snippet.get('channelTitle', '')}")
            print(f"itemCount: {details.get('itemCount', 0)}")
            print("---")

    result = youtube_api("playlistItems", {
        "part": "snippet,contentDetails",
        "playlistId": args.playlist_id,
        "maxResults": min(args.limit, 50),
    })

    items = result.get("items", [])
    total = result.get("pageInfo", {}).get("totalResults", 0)

    print(f"total: {total}")
    print(f"videos[{len(items)}]{{videoId,title,channel,position}}:")

    for item in items:
        snippet = item.get("snippet", {})
        video_id = snippet.get("resourceId", {}).get("videoId", "")
        title = snippet.get("title", "").replace(",", "，")[:60]
        channel = snippet.get("videoOwnerChannelTitle", "")
        position = snippet.get("position", 0)
        print(f"  {video_id},{title},{channel},{position}")


if __name__ == "__main__":
    main()
