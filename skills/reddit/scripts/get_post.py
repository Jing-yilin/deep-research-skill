#!/usr/bin/env python3
"""
Get a post with comments
Usage: python3 scripts/get_post.py POST_ID --comments 20
"""
import argparse
from reddit_api import api_get, clean_post, print_post, print_comments_list
from toon_format import encode as toon_encode


def main():
    parser = argparse.ArgumentParser(description="Get Reddit post with comments")
    parser.add_argument("post_id", help="Post ID (e.g., abc123)")
    parser.add_argument("--comments", "-c", type=int, default=20, help="Max comments")
    args = parser.parse_args()

    data = api_get(f"comments/{args.post_id}", {"limit": args.comments})

    if not isinstance(data, list) or len(data) < 2:
        print("post_not_found: true")
        return

    post_listing = data[0].get("data", {}).get("children", [])
    if post_listing:
        post = clean_post(post_listing[0])
        print_post(post)

    comments_listing = data[1].get("data", {}).get("children", [])
    if comments_listing:
        print_comments_list(comments_listing[:args.comments])


if __name__ == "__main__":
    main()
