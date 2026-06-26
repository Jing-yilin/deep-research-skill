# Dependencies — reddit

## Runtime Environment

Managed via **uv** with an isolated `.venv` (Python 3.12).

```bash
uv sync          # create/update venv
uv run python scripts/search_posts.py "keyword"
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
