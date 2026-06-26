#!/usr/bin/env python3
"""
Get video transcript using TranscriptAPI.com
Usage: python3 scripts/get_transcript.py VIDEO_ID
"""
import argparse
import sys
from youtube_api import parse_video_id, transcript_api


def main():
    parser = argparse.ArgumentParser(description="Get YouTube video transcript")
    parser.add_argument("video", help="Video ID or URL")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--metadata", "-m", action="store_true", 
                        help="Include video metadata")
    parser.add_argument("--no-timestamp", action="store_true",
                        help="Exclude timestamps")
    args = parser.parse_args()

    video_id = parse_video_id(args.video)
    
    result = transcript_api(
        video_id,
        format=args.format,
        include_timestamp=not args.no_timestamp,
        send_metadata=args.metadata,
    )

    print(f"videoId: {result.get('video_id', video_id)}")
    print(f"language: {result.get('language', 'unknown')}")
    
    if args.metadata and "metadata" in result:
        meta = result["metadata"]
        print(f"title: {meta.get('title', '')}")
        print(f"author: {meta.get('author_name', '')}")

    print("---")
    
    transcript = result.get("transcript", [])
    if args.format == "text" or isinstance(transcript, str):
        print(transcript)
    else:
        for segment in transcript[:100]:
            if args.no_timestamp:
                print(segment.get("text", ""))
            else:
                start = segment.get("start", 0)
                text = segment.get("text", "")
                print(f"[{start:.1f}s] {text}")
        
        if len(transcript) > 100:
            print(f"... ({len(transcript) - 100} more segments)")


if __name__ == "__main__":
    main()
