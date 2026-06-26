---
name: reddit
description: Search and retrieve content from Reddit. Get posts, comments, subreddit info, and user profiles via the public JSON API and ScrapeCreators. Supports write operations (post, comment, edit, delete) via Composio.
triggers:
  - "reddit"
  - "subreddit"
  - "r/"
---

# Reddit Skill

All output is in **TOON format** (compact, token-efficient).

Read Reddit content via the public JSON API (no auth). Enhanced endpoints use ScrapeCreators (`SCRAPECREATORS_API_KEY`). Write operations use Composio SDK v1 (`COMPOSIO_API_KEY`).

All commands run from: `/Users/yilin/Developer/DailyTasks/.agents/skills/reddit`

## Read Operations (no auth required)

### Get posts from subreddit
```bash
uv run python scripts/get_posts.py <subreddit> [--sort hot|new|top|rising|controversial] [--time hour|day|week|month|year|all] [--limit N]
```
```bash
uv run python scripts/get_posts.py ClaudeAI --sort top --time week --limit 10
# 'best' sort requires SCRAPECREATORS_API_KEY:
uv run python scripts/get_posts.py ClaudeAI --sort best --limit 10
```

### Search posts
```bash
uv run python scripts/search_posts.py "<query>" [--subreddit NAME] [--sort relevance|hot|top|new|comments|comment_count] [--limit N] [--trim]
```
```bash
uv run python scripts/search_posts.py "MCP server" --subreddit ClaudeAI --limit 10
# 'comment_count' sort requires SCRAPECREATORS_API_KEY:
uv run python scripts/search_posts.py "Claude Code" --sort comment_count --trim
```

### Get subreddit info
```bash
uv run python scripts/get_subreddit.py <subreddit>
```

### Get specific post + comments (by post ID)
```bash
uv run python scripts/get_post.py <post_id> [--comments N]
```

### Get post comments by URL (ScrapeCreators — cursor pagination, nested replies)
```bash
uv run python scripts/get_post_comments_url.py "<post_url>" [--cursor <cursor>]
```
```bash
uv run python scripts/get_post_comments_url.py "https://www.reddit.com/r/ClaudeAI/comments/abc123/title/"
```

### Get user profile
```bash
uv run python scripts/get_user.py <username> [--posts N]
```

### Get subreddit rules (read before posting)
```bash
uv run python scripts/get_rules.py <subreddit>
```

### Get available post flairs
```bash
uv run python scripts/get_flairs.py <subreddit>
```

### Post with image
Composio's Reddit tool does **not** support native image uploads. Two workarounds:

**Option A — Imgur link post** (recommended):
```bash
# 1. Upload image to Imgur manually or via API, get public URL
# 2. Post as a link post:
uv run python scripts/reddit_composio.py --user-id <account> create-post \
  --subreddit <sub> \
  --title "Title" \
  --url "https://i.imgur.com/xxxxx.png"
```

**Option B — Markdown image in text post** (shows inline on some clients):
```bash
uv run python scripts/reddit_composio.py --user-id <account> create-post \
  --subreddit <sub> \
  --title "Title" \
  --text "Description\n\n[View image](https://i.imgur.com/xxxxx.png)"
```

## ScrapeCreators Operations (requires `SCRAPECREATORS_API_KEY`)

1 credit per call. Check balance: `curl -s https://api.scrapecreators.com/v1/credit/balance -H "x-api-key: $SCRAPECREATORS_API_KEY"`

### Get rich subreddit details
Includes `weekly_active_users`, `weekly_contributions`, `submit_text`, `icon_img`, `header_img`, `advertiser_category`.
```bash
uv run python scripts/get_subreddit_details.py <subreddit>
```
```bash
uv run python scripts/get_subreddit_details.py ClaudeAI
```

### Search within a subreddit (posts + comments + media)
```bash
uv run python scripts/search_subreddit.py <subreddit> "<query>" [--type posts|comments|media|all] [--cursor <cursor>]
```
```bash
uv run python scripts/search_subreddit.py ClaudeAI "MCP server" --type all
```

## Write Operations (Composio required)

Uses `scripts/reddit_composio.py`. Requires `COMPOSIO_API_KEY` in env.

### Pre-posting workflow (always do this first)

```bash
# 1. Check rules — critical, each sub is different
uv run python scripts/get_rules.py <subreddit>

# 2. Get available flairs (many subs require one)
uv run python scripts/get_flairs.py <subreddit>

# 3. Browse recent posts to understand tone
uv run python scripts/get_posts.py <subreddit> --limit 10
```

### Create a post

```bash
uv run python scripts/reddit_composio.py create-post \
  --subreddit ClaudeAI \
  --title "Post title" \
  --text "Post body (markdown supported)" \
  --flair-id "<id from get_flairs>"
```

### Post a comment

```bash
uv run python scripts/reddit_composio.py post-comment \
  --thing-id t3_<post_id> \
  --text "Comment text"
```

### Edit a post or comment

```bash
uv run python scripts/reddit_composio.py edit \
  --thing-id t3_<post_id> \
  --text "Updated text"
```

### Search + flair operations

```bash
uv run python scripts/reddit_composio.py search-posts --query "Claude Code" --limit 5
uv run python scripts/reddit_composio.py search-subreddits --query "AI tools"
uv run python scripts/reddit_composio.py list-post-flairs --subreddit ClaudeAI
```

All available commands: `uv run python scripts/reddit_composio.py --help`

## Auth Setup

Reddit connected via Composio dashboard: https://dashboard.composio.dev

```bash
# Re-authorize if token expires
uv run composio add reddit
```

Default `user_id` is `"default"`. Override with `--user-id` or `$COMPOSIO_USER_ID` env var.

## Notes

- Rate limit: 100 requests/minute (public API)
- Post IDs: from URL `reddit.com/r/sub/comments/<id>/title/`
- `thing_id` prefix: `t1_` = comment, `t3_` = post
- Many subreddits require flair — always run `get_flairs.py` before posting
- Always check rules before posting to avoid removal
- ScrapeCreators subreddit names are case-sensitive: use `AskReddit` not `askreddit`

## r/ClaudeAI Flair Reference

| Flair | ID |
|-------|----|
| Claude Code Workflow | `110dc408-4b90-11f1-8f47-cabda7332b3b` |
| Skills | `98072542-4d13-11f1-9971-c6b2ecb5416b` |
| Built with Claude | `b1f30a12-6938-11f0-aad7-6eea404d38fd` |
| Claude Code | `a35c0c72-4094-11f1-9d0f-1a7a82a8c650` |
| MCP | `be3bf80a-adf0-11ef-a270-f27e2f71f38f` |
| Feedback | `3a88739e-2538-11ef-8e1b-8a15317f9ddd` |
| Productivity | `e4304450-2540-11ef-b8c8-8a15317f9ddd` |
| Promotion | `66cfe0da-2539-11ef-815a-8a28f6cc7364` |
