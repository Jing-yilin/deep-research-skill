# Dependencies — twitter

## Runtime Environment

Managed via **uv** with an isolated `.venv` (Python 3.12).

```bash
uv sync          # create/update venv
uv run python scripts/search_tweets.py "keyword"
```

## Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `composio-core` | `>=0.6.0` | Composio SDK for Twitter/X via OAuth |
| `requests` | `>=2.31.0` | HTTP client for twitterapi.io REST calls |

## Auth Setup

### twitterapi.io (primary)
Set `TWITTER_API_KEY` in `~/.zshrc`:
```bash
export TWITTER_API_KEY="your_key_here"
```

### Composio (alternative)
```bash
composio login
composio add twitter
```
