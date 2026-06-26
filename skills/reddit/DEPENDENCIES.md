# Dependencies — reddit

## Runtime Environment

In this bundle, all Python skills share **one** uv environment defined by the
repo-root `pyproject.toml` (Python 3.12). Set it up once at the repo root:

```bash
uv sync                     # repo root — creates the shared ./.venv
source .venv/bin/activate
python3 skills/reddit/scripts/search_posts.py "keyword"
```

## Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `composio-core` | `>=0.6.0` | Composio SDK for Reddit via OAuth |
| `requests` | `>=2.31.0` | HTTP client for Reddit public JSON API |

## Auth Setup

Reddit public API (no auth) works for reading public posts/subreddits.

Composio-based operations require:
```bash
composio login
composio add reddit
```
