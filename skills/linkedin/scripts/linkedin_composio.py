#!/usr/bin/env python3
"""LinkedIn write operations using Composio SDK (v1 API)."""

import argparse
import mimetypes
import os
import sys

import requests
from composio import Composio
from toon_format import encode as toon_encode

DEFAULT_USER_ID = os.environ.get("COMPOSIO_USER_ID", "yilin")


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
    return result


# ── Profile ───────────────────────────────────────────────────────────────────

def get_my_info(user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_MY_INFO", {}, user_id)

def get_person(person_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_PERSON", {"person_id": person_id}, user_id)

def get_company_info(user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_COMPANY_INFO", {}, user_id)

def get_network_size(org_urn: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_NETWORK_SIZE", {"organizationUrn": org_urn}, user_id)

# ── Posts ─────────────────────────────────────────────────────────────────────

def create_post(text: str, visibility: str = "PUBLIC", user_id: str = DEFAULT_USER_ID):
    """Create a text post on LinkedIn."""
    _exec("LINKEDIN_CREATE_LINKED_IN_POST", {
        "commentary": text,
        "visibility": visibility,
        "lifecycleState": "PUBLISHED",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        }
    }, user_id)

def create_article_share(url: str, title: str = None, description: str = None,
                          visibility: str = "PUBLIC", user_id: str = DEFAULT_USER_ID):
    """Share a URL/article on LinkedIn."""
    params = {"shareUrl": url, "visibility": visibility}
    if title:
        params["title"] = title
    if description:
        params["description"] = description
    _exec("LINKEDIN_CREATE_ARTICLE_OR_URL_SHARE", params, user_id)

def delete_post(share_id: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_DELETE_LINKED_IN_POST", {"share_id": share_id}, user_id)

def get_post_content(post_urn: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_POST_CONTENT", {"postUrn": post_urn}, user_id)

# ── Comments ──────────────────────────────────────────────────────────────────

def create_comment(post_urn: str, text: str, user_id: str = DEFAULT_USER_ID):
    """Comment on a LinkedIn post."""
    _exec("LINKEDIN_CREATE_COMMENT_ON_POST", {
        "shareUrn": post_urn,
        "message": {"text": text}
    }, user_id)

def list_reactions(entity_urn: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_LIST_REACTIONS", {"entityUrn": entity_urn}, user_id)

# ── Stats ─────────────────────────────────────────────────────────────────────

def get_share_stats(org_urn: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_SHARE_STATS", {"organizationUrn": org_urn}, user_id)

def get_org_page_stats(org_urn: str, user_id: str = DEFAULT_USER_ID):
    _exec("LINKEDIN_GET_ORG_PAGE_STATS", {"organizationUrn": org_urn}, user_id)

# ── Images ────────────────────────────────────────────────────────────────────

def init_image_upload(owner_urn: str = None, user_id: str = DEFAULT_USER_ID):
    """Initialize image upload — returns presigned URL and image URN."""
    if not owner_urn:
        # Auto-fetch person ID
        c = get_client()
        info = c.tools.execute(slug="LINKEDIN_GET_MY_INFO", user_id=user_id,
                               arguments={}, dangerously_skip_version_check=True)
        person_id = info.get("data", {}).get("id")
        owner_urn = f"urn:li:person:{person_id}"
    result = _exec("LINKEDIN_INITIALIZE_IMAGE_UPLOAD", {"owner": owner_urn}, user_id)
    return result


def create_post_with_image(file_path: str, text: str, visibility: str = "PUBLIC",
                            user_id: str = DEFAULT_USER_ID):
    """Upload a local image and create a LinkedIn post with it."""
    if not os.path.exists(file_path):
        print(f"error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    c = get_client()

    # Step 1: Get person ID
    info = c.tools.execute(slug="LINKEDIN_GET_MY_INFO", user_id=user_id,
                           arguments={}, dangerously_skip_version_check=True)
    person_id = info.get("data", {}).get("id")
    owner_urn = f"urn:li:person:{person_id}"
    author_urn = owner_urn

    # Step 2: Initialize image upload
    init_result = c.tools.execute(
        slug="LINKEDIN_INITIALIZE_IMAGE_UPLOAD",
        user_id=user_id,
        arguments={"owner": owner_urn},
        dangerously_skip_version_check=True,
    )
    image_urn = init_result.get("data", {}).get("image")
    upload_url = init_result.get("data", {}).get("upload_url")
    if not image_urn or not upload_url:
        print("error: failed to initialize image upload", file=sys.stderr)
        print(toon_encode(init_result))
        sys.exit(1)

    print(f"image_urn: {image_urn}")

    # Step 3: Upload the file
    mimetype = mimetypes.guess_type(file_path)[0] or "image/jpeg"
    with open(file_path, "rb") as f:
        resp = requests.put(upload_url, data=f, headers={"Content-Type": mimetype})
    if resp.status_code not in (200, 201):
        print(f"error: image upload failed: HTTP {resp.status_code}", file=sys.stderr)
        print(resp.text[:300], file=sys.stderr)
        sys.exit(1)
    print(f"upload: OK ({resp.status_code})")

    # Step 4: Create post with image URN
    result = c.tools.execute(
        slug="LINKEDIN_CREATE_LINKED_IN_POST",
        user_id=user_id,
        arguments={
            "author": author_urn,
            "commentary": text,
            "visibility": visibility,
            "lifecycleState": "PUBLISHED",
            "content": {"media": {"id": image_urn}},
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
        },
        dangerously_skip_version_check=True,
    )
    print(toon_encode(result))


def main():
    parser = argparse.ArgumentParser(description="LinkedIn write operations via Composio")
    parser.add_argument("--user-id", default=DEFAULT_USER_ID,
                        help="Composio user/entity ID (default: $COMPOSIO_USER_ID or 'yilin')")
    sub = parser.add_subparsers(dest="command", required=True)

    # Profile
    sub.add_parser("get-my-info", help="Get authenticated user's LinkedIn profile")

    p = sub.add_parser("get-person", help="Get a LinkedIn member's profile by person ID")
    p.add_argument("--person-id", required=True)

    sub.add_parser("get-company-info", help="Get orgs where you have admin roles")

    p = sub.add_parser("get-network-size", help="Get follower count for an org")
    p.add_argument("--org-urn", required=True, help="e.g. urn:li:organization:12345")

    # Posts
    p = sub.add_parser("create-post", help="Create a text post on LinkedIn")
    p.add_argument("--text", "-t", required=True, help="Post content (markdown supported)")
    p.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "CONNECTIONS", "LOGGED_IN"])

    p = sub.add_parser("share-url", help="Share a URL/article on LinkedIn")
    p.add_argument("--url", required=True)
    p.add_argument("--title", help="Optional title override")
    p.add_argument("--description", help="Optional description override")
    p.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "CONNECTIONS", "LOGGED_IN"])

    p = sub.add_parser("delete-post", help="Delete a LinkedIn post")
    p.add_argument("--share-id", required=True)

    p = sub.add_parser("get-post", help="Get post content by URN")
    p.add_argument("--post-urn", required=True, help="e.g. urn:li:share:12345")

    # Comments
    p = sub.add_parser("comment", help="Comment on a LinkedIn post")
    p.add_argument("--post-urn", required=True, help="e.g. urn:li:share:12345")
    p.add_argument("--text", "-t", required=True)

    p = sub.add_parser("list-reactions", help="List reactions on a post/entity")
    p.add_argument("--entity-urn", required=True)

    # Stats
    p = sub.add_parser("share-stats", help="Get share statistics for an org")
    p.add_argument("--org-urn", required=True)

    p = sub.add_parser("page-stats", help="Get page statistics for an org")
    p.add_argument("--org-urn", required=True)

    # Images
    p = sub.add_parser("create-post-image", help="Upload a local image and create a LinkedIn post")
    p.add_argument("--file", "-f", required=True, help="Path to local image file (jpg/png/gif)")
    p.add_argument("--text", "-t", required=True, help="Post text (up to 3000 chars)")
    p.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "CONNECTIONS", "LOGGED_IN"])

    sub.add_parser("init-image-upload", help="Initialize image upload, get presigned URL + image URN")

    args = parser.parse_args()
    uid = args.user_id

    dispatch = {
        "get-my-info":       lambda: get_my_info(uid),
        "get-person":        lambda: get_person(args.person_id, uid),
        "get-company-info":  lambda: get_company_info(uid),
        "get-network-size":  lambda: get_network_size(args.org_urn, uid),
        "create-post":       lambda: create_post(args.text, args.visibility, uid),
        "share-url":         lambda: create_article_share(args.url, getattr(args, "title", None), getattr(args, "description", None), args.visibility, uid),
        "delete-post":       lambda: delete_post(args.share_id, uid),
        "get-post":          lambda: get_post_content(args.post_urn, uid),
        "comment":           lambda: create_comment(args.post_urn, args.text, uid),
        "list-reactions":    lambda: list_reactions(args.entity_urn, uid),
        "share-stats":       lambda: get_share_stats(args.org_urn, uid),
        "page-stats":        lambda: get_org_page_stats(args.org_urn, uid),
        "create-post-image": lambda: create_post_with_image(args.file, args.text, args.visibility, uid),
        "init-image-upload": lambda: init_image_upload(None, uid),
    }
    dispatch[args.command]()


if __name__ == "__main__":
    main()
