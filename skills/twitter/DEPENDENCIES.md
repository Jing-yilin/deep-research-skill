# Dependencies — twitter

## Runtime Environment

In this bundle, all Python skills share **one** uv environment defined by the
repo-root `pyproject.toml` (Python 3.12). Set it up once at the repo root:

```bash
uv sync                     # repo root — creates the shared ./.venv
source .venv/bin/activate
python3 skills/twitter/scripts/search_tweets.py "keyword"
```

## Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `composio-core` | `>=0.6.0` | Composio SDK for Twitter/X via OAuth |
| `requests` | `>=2.31.0` | HTTP client for twitterapi.io REST calls |

## Auth Setup

### twitterapi.io (primary)
Set `TWITTERAPI_API_KEY` in `~/.zshrc` (this is the name the scripts read):
```bash
export TWITTERAPI_API_KEY="your_key_here"
```

### Composio (alternative)
```bash
composio login
composio add twitter
```
