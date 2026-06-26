#!/usr/bin/env python3
"""Reddit write operations using Composio SDK (v1 API)."""

import argparse
import os
import sys

from composio import Composio
from toon_format import encode as toon_encode

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
    print(toon_encode(result))

# ── Read ──────────────────────────────────────────────────────────────────────

def get_posts(subreddit: str, size: int = 5, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_RETRIEVE_REDDIT_POST", {"subreddit": subreddit, "size": size}, user_id)

def get_post(post_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_RETRIEVE_SPECIFIC_COMMENT", {"id": post_id}, user_id)

def get_comments(article_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_RETRIEVE_POST_COMMENTS", {"article": article_id}, user_id)

def get_listing(sort: str, limit: int = 25, time_filter: str = None, after: str = None, user_id: str = DEFAULT_USER_ID):
    params = {"sort": sort, "limit": limit}
    if time_filter:
        params["time_filter"] = time_filter
    if after:
        params["after"] = after
    _exec("REDDIT_GET", params, user_id)

def get_top(subreddit: str, time_filter: str = "all", limit: int = 25, after: str = None, user_id: str = DEFAULT_USER_ID):
    params = {"subreddit": subreddit, "t": time_filter, "limit": limit}
    if after:
        params["after"] = after
    _exec("REDDIT_GET_R_TOP", params, user_id)

def get_random(subreddit: str = None, user_id: str = DEFAULT_USER_ID):
    params = {}
    if subreddit:
        params["subreddit"] = subreddit
    _exec("REDDIT_GET_RANDOM", params, user_id)

def get_user(username: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_GET_REDDIT_USER_ABOUT", {"username": username}, user_id)

def get_subreddit_rules(subreddit: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_GET_SUBREDDIT_RULES", {"subreddit": subreddit, "raw_json": True}, user_id)

# ── Write ─────────────────────────────────────────────────────────────────────

def create_post(subreddit: str, title: str, text: str = None, url: str = None, flair_id: str = None, user_id: str = DEFAULT_USER_ID):
    params = {"subreddit": subreddit, "title": title}
    if text:
        params["text"] = text
        params["kind"] = "self"
    if url:
        params["url"] = url
        params["kind"] = "link"
    if flair_id:
        params["flair_id"] = flair_id
    _exec("REDDIT_CREATE_REDDIT_POST", params, user_id)

def post_comment(thing_id: str, text: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_POST_REDDIT_COMMENT", {"thing_id": thing_id, "text": text}, user_id)

def edit(thing_id: str, text: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_EDIT_REDDIT_COMMENT_OR_POST", {"thing_id": thing_id, "text": text}, user_id)

def delete_post(post_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_DELETE_REDDIT_POST", {"id": post_id}, user_id)

def delete_comment(comment_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_DELETE_REDDIT_COMMENT", {"id": comment_id}, user_id)

# ── Search ────────────────────────────────────────────────────────────────────

def search_posts(query: str, limit: int = 5, sort: str = "relevance", restrict_sr: bool = True, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_SEARCH_ACROSS_SUBREDDITS", {"search_query": query, "limit": limit, "sort": sort, "restrict_sr": restrict_sr}, user_id)

def search_subreddits(query: str, limit: int = 25, sort: str = "relevance", user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_GET_SUBREDDITS_SEARCH", {"q": query, "limit": limit, "sort": sort}, user_id)

# ── Flair ─────────────────────────────────────────────────────────────────────

def get_link_flairs(subreddit: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_GET_R_SUBREDDIT_LINK_FLAIR_V2", {"subreddit": subreddit}, user_id)

def list_post_flairs(subreddit: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_LIST_SUBREDDIT_POST_FLAIRS", {"subreddit": subreddit}, user_id)

def get_user_flair(subreddit: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_GET_USER_FLAIR", {"subreddit": subreddit}, user_id)

# ── Utility ───────────────────────────────────────────────────────────────────

def get_preferences(fields: str = None, user_id: str = DEFAULT_USER_ID):
    params = {}
    if fields:
        params["fields"] = fields
    _exec("REDDIT_GET_ME_PREFS", params, user_id)

def check_username(username: str, user_id: str = DEFAULT_USER_ID):
    _exec("REDDIT_GET_USERNAME_AVAILABLE", {"user": username}, user_id)


def main():
    parser = argparse.ArgumentParser(description="Reddit operations via Composio")
    parser.add_argument("--user-id", default=DEFAULT_USER_ID, help="Composio user/entity ID (default: $COMPOSIO_USER_ID or 'default')")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Read
    p = subparsers.add_parser("get-posts", help="Get hot posts from subreddit")
    p.add_argument("--subreddit", "-s", required=True)
    p.add_argument("--size", type=int, default=5)

    p = subparsers.add_parser("get-post", help="Get specific post/comment by ID")
    p.add_argument("--id", required=True)

    p = subparsers.add_parser("get-comments", help="Get comments for a post")
    p.add_argument("--article", required=True)

    p = subparsers.add_parser("get-listing", help="Get Reddit listing by sort")
    p.add_argument("--sort", required=True, choices=["hot", "new", "top", "rising", "controversial"])
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"])
    p.add_argument("--after")

    p = subparsers.add_parser("get-top", help="Get top posts from subreddit")
    p.add_argument("--subreddit", "-s", required=True)
    p.add_argument("--time", default="all", choices=["hour", "day", "week", "month", "year", "all"])
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--after")

    p = subparsers.add_parser("get-random", help="Get random post")
    p.add_argument("--subreddit", "-s")

    p = subparsers.add_parser("get-user", help="Get user information")
    p.add_argument("--username", "-u", required=True)

    p = subparsers.add_parser("get-subreddit-rules", help="Get subreddit rules")
    p.add_argument("--subreddit", "-s", required=True)

    # Write
    p = subparsers.add_parser("create-post", help="Create a new post")
    p.add_argument("--subreddit", "-s", required=True)
    p.add_argument("--title", "-t", required=True)
    p.add_argument("--text", help="Text for self post")
    p.add_argument("--url", help="URL for link post")
    p.add_argument("--flair-id")

    p = subparsers.add_parser("post-comment", help="Post a comment")
    p.add_argument("--thing-id", required=True)
    p.add_argument("--text", "-t", required=True)

    p = subparsers.add_parser("edit", help="Edit comment or post")
    p.add_argument("--thing-id", required=True)
    p.add_argument("--text", "-t", required=True)

    p = subparsers.add_parser("delete-post")
    p.add_argument("--id", required=True)

    p = subparsers.add_parser("delete-comment")
    p.add_argument("--id", required=True)

    # Search
    p = subparsers.add_parser("search-posts")
    p.add_argument("--query", "-q", required=True)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--sort", default="relevance", choices=["relevance", "hot", "top", "new", "comments"])
    p.add_argument("--restrict-sr", type=bool, default=True)

    p = subparsers.add_parser("search-subreddits")
    p.add_argument("--query", "-q", required=True)
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--sort", default="relevance")

    # Flair
    p = subparsers.add_parser("get-link-flairs")
    p.add_argument("--subreddit", "-s", required=True)

    p = subparsers.add_parser("list-post-flairs")
    p.add_argument("--subreddit", "-s", required=True)

    p = subparsers.add_parser("get-user-flair")
    p.add_argument("--subreddit", "-s", required=True)

    # Utility
    p = subparsers.add_parser("get-preferences")
    p.add_argument("--fields")

    p = subparsers.add_parser("check-username")
    p.add_argument("--username", "-u", required=True)

    args = parser.parse_args()
    uid = args.user_id

    dispatch = {
        "get-posts":           lambda: get_posts(args.subreddit, args.size, uid),
        "get-post":            lambda: get_post(args.id, uid),
        "get-comments":        lambda: get_comments(args.article, uid),
        "get-listing":         lambda: get_listing(args.sort, args.limit, args.time, args.after, uid),
        "get-top":             lambda: get_top(args.subreddit, args.time, args.limit, args.after, uid),
        "get-random":          lambda: get_random(getattr(args, "subreddit", None), uid),
        "get-user":            lambda: get_user(args.username, uid),
        "get-subreddit-rules": lambda: get_subreddit_rules(args.subreddit, uid),
        "create-post":         lambda: create_post(args.subreddit, args.title, args.text, args.url, getattr(args, "flair_id", None), uid),
        "post-comment":        lambda: post_comment(args.thing_id, args.text, uid),
        "edit":                lambda: edit(args.thing_id, args.text, uid),
        "delete-post":         lambda: delete_post(args.id, uid),
        "delete-comment":      lambda: delete_comment(args.id, uid),
        "search-posts":        lambda: search_posts(args.query, args.limit, args.sort, args.restrict_sr, uid),
        "search-subreddits":   lambda: search_subreddits(args.query, args.limit, args.sort, uid),
        "get-link-flairs":     lambda: get_link_flairs(args.subreddit, uid),
        "list-post-flairs":    lambda: list_post_flairs(args.subreddit, uid),
        "get-user-flair":      lambda: get_user_flair(args.subreddit, uid),
        "get-preferences":     lambda: get_preferences(getattr(args, "fields", None), uid),
        "check-username":      lambda: check_username(args.username, uid),
    }
    dispatch[args.command]()


if __name__ == "__main__":
    main()
