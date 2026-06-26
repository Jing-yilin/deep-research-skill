#!/usr/bin/env python3
"""Twitter write operations using Composio SDK (v1 API)."""

import argparse
import json
import os
import sys

from composio import Composio

DEFAULT_USER_ID = os.environ.get("COMPOSIO_USER_ID", "default")

def get_client() -> Composio:
    return Composio()

def _exec(slug: str, arguments: dict, user_id: str = DEFAULT_USER_ID):
    c = get_client()
    result = c.tools.execute(
        slug=slug,
        user_id=user_id,
        arguments=arguments,
        dangerously_skip_version_check=True,
    )
    print(json.dumps(result, indent=2, default=str))

def _get_user_id_from_username(username: str, user_id: str) -> str:
    """Resolve @username to Twitter numeric ID via Composio."""
    c = get_client()
    result = c.tools.execute(
        slug="TWITTER_USER_LOOKUP_BY_USERNAME",
        user_id=user_id,
        arguments={"username": username},
        dangerously_skip_version_check=True,
    )
    if not result.get("successful") or "data" not in result:
        print(f"Error: Could not find user @{username}", file=sys.stderr)
        print(json.dumps(result, indent=2, default=str), file=sys.stderr)
        sys.exit(1)
    return result["data"]["id"]

# ── Tweets ────────────────────────────────────────────────────────────────────

def create_tweet(text: str, media_ids: str = None, reply_to: str = None, quote_tweet: str = None, user_id: str = DEFAULT_USER_ID):
    params = {"text": text}
    if media_ids:
        params["media_media_ids"] = [mid.strip() for mid in media_ids.split(",")]
    if reply_to:
        params["reply_in_reply_to_tweet_id"] = reply_to
    if quote_tweet:
        params["quote_tweet_id"] = quote_tweet
    _exec("TWITTER_CREATION_OF_A_POST", params, user_id)

def delete_tweet(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_POST_DELETE_BY_POST_ID", {"id": tweet_id}, user_id)

def like_tweet(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_USER_LIKE_POST", {"tweet_id": tweet_id}, user_id)

def unlike_tweet(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_UNLIKE_POST", {"tweet_id": tweet_id}, user_id)

def retweet(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_REPOST_A_POST", {"source_tweet_id": tweet_id}, user_id)

def unretweet(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_UNRETWEET_POST", {"source_tweet_id": tweet_id}, user_id)

# ── DM ────────────────────────────────────────────────────────────────────────

def send_dm(username: str, text: str, user_id: str = DEFAULT_USER_ID):
    participant_id = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_SEND_A_NEW_MESSAGE_TO_A_USER", {"participant_id": participant_id, "text": text}, user_id)

# ── Media ─────────────────────────────────────────────────────────────────────

def upload_media(file_path: str, user_id: str = DEFAULT_USER_ID):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    _exec("TWITTER_UPLOAD_MEDIA", {"media": {"file_path": file_path}}, user_id)

def upload_large_media(file_path: str, media_category: str = "tweet_video", user_id: str = DEFAULT_USER_ID):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    _exec("TWITTER_UPLOAD_LARGE_MEDIA", {"local_file_path": file_path, "media_category": media_category}, user_id)

# ── Follow / Unfollow ─────────────────────────────────────────────────────────

def follow_user(username: str, user_id: str = DEFAULT_USER_ID):
    target = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_FOLLOW_USER", {"target_user_id": target}, user_id)

def unfollow_user(username: str, user_id: str = DEFAULT_USER_ID):
    target = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_UNFOLLOW_USER", {"target_user_id": target}, user_id)

# ── Bookmarks ─────────────────────────────────────────────────────────────────

def add_bookmark(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_ADD_POST_TO_BOOKMARKS", {"tweet_id": tweet_id}, user_id)

def remove_bookmark(tweet_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("TWITTER_REMOVE_A_BOOKMARKED_POST", {"tweet_id": tweet_id}, user_id)

# ── Block / Mute ──────────────────────────────────────────────────────────────

def block_user(username: str, user_id: str = DEFAULT_USER_ID):
    target = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_BLOCK_USER_BY_USER_ID", {"target_user_id": target}, user_id)

def unblock_user(username: str, user_id: str = DEFAULT_USER_ID):
    target = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_UNBLOCK_USER_BY_USER_ID", {"target_user_id": target}, user_id)

def mute_user(username: str, user_id: str = DEFAULT_USER_ID):
    target = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_MUTE_USER_BY_USER_ID", {"target_user_id": target}, user_id)

def unmute_user(username: str, user_id: str = DEFAULT_USER_ID):
    target = _get_user_id_from_username(username, user_id)
    _exec("TWITTER_UNMUTE_USER_BY_USER_ID", {"target_user_id": target}, user_id)


def main():
    parser = argparse.ArgumentParser(
        description="Twitter write operations via Composio",
        epilog=(
            "Examples:\n"
            "  twitter_composio.py create-tweet --text 'Hello World!'\n"
            "  twitter_composio.py create-tweet --text 'Check this!' --media 1234567890\n"
            "  twitter_composio.py send-dm --username elonmusk --text 'Hi!'\n"
            "  twitter_composio.py upload-media --file image.png"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--user-id", default=DEFAULT_USER_ID, help="Composio user/entity ID (default: $COMPOSIO_USER_ID or 'default')")
    sub = parser.add_subparsers(dest="command", required=True)

    # Tweets
    p = sub.add_parser("create-tweet", help="Post a tweet")
    p.add_argument("--text", required=True, help="Tweet text (≤280 chars)")
    p.add_argument("--media", help="Comma-separated media IDs")
    p.add_argument("--reply-to", help="Tweet ID to reply to")
    p.add_argument("--quote", help="Tweet ID to quote")

    p = sub.add_parser("delete-tweet")
    p.add_argument("--id", required=True)

    p = sub.add_parser("like")
    p.add_argument("--id", required=True)

    p = sub.add_parser("unlike")
    p.add_argument("--id", required=True)

    p = sub.add_parser("retweet")
    p.add_argument("--id", required=True)

    p = sub.add_parser("unretweet")
    p.add_argument("--id", required=True)

    # DM
    p = sub.add_parser("send-dm")
    p.add_argument("--username", required=True)
    p.add_argument("--text", required=True)

    # Media
    p = sub.add_parser("upload-media", help="Upload image (<5 MB)")
    p.add_argument("--file", required=True)

    p = sub.add_parser("upload-large-media", help="Upload video/GIF or large file")
    p.add_argument("--file", required=True)
    p.add_argument("--category", default="tweet_video", choices=["tweet_image", "tweet_video", "tweet_gif"])

    # Follow/Unfollow
    p = sub.add_parser("follow")
    p.add_argument("--username", required=True)

    p = sub.add_parser("unfollow")
    p.add_argument("--username", required=True)

    # Bookmarks
    p = sub.add_parser("add-bookmark")
    p.add_argument("--id", required=True)

    p = sub.add_parser("remove-bookmark")
    p.add_argument("--id", required=True)

    # Block / Mute
    p = sub.add_parser("block")
    p.add_argument("--username", required=True)

    p = sub.add_parser("unblock")
    p.add_argument("--username", required=True)

    p = sub.add_parser("mute")
    p.add_argument("--username", required=True)

    p = sub.add_parser("unmute")
    p.add_argument("--username", required=True)

    args = parser.parse_args()
    uid = args.user_id

    dispatch = {
        "create-tweet":      lambda: create_tweet(args.text, getattr(args, "media", None), getattr(args, "reply_to", None), getattr(args, "quote", None), uid),
        "delete-tweet":      lambda: delete_tweet(args.id, uid),
        "like":              lambda: like_tweet(args.id, uid),
        "unlike":            lambda: unlike_tweet(args.id, uid),
        "retweet":           lambda: retweet(args.id, uid),
        "unretweet":         lambda: unretweet(args.id, uid),
        "send-dm":           lambda: send_dm(args.username, args.text, uid),
        "upload-media":      lambda: upload_media(args.file, uid),
        "upload-large-media": lambda: upload_large_media(args.file, args.category, uid),
        "follow":            lambda: follow_user(args.username, uid),
        "unfollow":          lambda: unfollow_user(args.username, uid),
        "add-bookmark":      lambda: add_bookmark(args.id, uid),
        "remove-bookmark":   lambda: remove_bookmark(args.id, uid),
        "block":             lambda: block_user(args.username, uid),
        "unblock":           lambda: unblock_user(args.username, uid),
        "mute":              lambda: mute_user(args.username, uid),
        "unmute":            lambda: unmute_user(args.username, uid),
    }
    dispatch[args.command]()


if __name__ == "__main__":
    main()
