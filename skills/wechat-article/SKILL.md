---
name: wechat-article
description: Download and export WeChat Official Account (微信公众号) articles. Use when the user wants to download, export, or fetch articles from WeChat public accounts, or needs to search for WeChat official accounts.
triggers:
  - "微信"
  - "公众号"
  - "WeChat"
  - "mp.weixin.qq.com"
  - "wechat article"
  - "微信文章"
---

# WeChat Article Exporter Skill

## Overview

This skill enables downloading and exporting articles from WeChat Official Accounts (微信公众号).

## Prerequisites

> **See [INSTALL.md](./INSTALL.md) for detailed installation instructions.**

Credentials stored in `~/.zshrc`:
```bash
export WECHAT_API_BASE_URL=<your-deployment-url>
export WECHAT_API_KEY=<your-api-key>
```

## Quick Start (CLI)

Use the `wxa` Rust CLI for fast, TOON-formatted output:

```bash
# Build (one-time)
cd cli && cargo build --release
# Binary: cli/target/release/wxa
```

### Search for an account
```bash
wxa search "AI Pioneer" --limit 5
```

### List articles from an account
```bash
wxa list MzI5NDk3OTMxNw== --limit 10
```

### Download article content
```bash
wxa download "https://mp.weixin.qq.com/s/xxx" --format markdown
wxa download "https://mp.weixin.qq.com/s/xxx" -o article.md
```

### Find source account from article URL
```bash
wxa source "https://mp.weixin.qq.com/s/xxx"
```

### Legacy Python Scripts

Python scripts in `scripts/` still work:
```bash
python scripts/search_account.py "keyword" --limit 5
python scripts/list_articles.py <fakeid> --limit 10
python scripts/download_article.py "https://mp.weixin.qq.com/s/xxx" --format markdown
```

## API Reference

> All commands use `$WECHAT_API_BASE_URL` and `$WECHAT_API_KEY` from shell environment.

### Authentication

Endpoints marked "需要认证" require API key via header: `X-Auth-Key: $WECHAT_API_KEY`

**Note**: API key is tied to website login session. When login expires, get a new key from browser cookies.

## Available Endpoints

### 1. Search Official Accounts (需要认证)

```
GET ${WECHAT_API_BASE_URL}/api/public/v1/account?keyword=<关键字>&begin=0&size=5
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| keyword | Yes | - | Search keyword (URL encoded) |
| begin | No | 0 | Start index |
| size | No | 5 | Number of results (max 20) |

### 2. Search Account by Article URL (需要认证)

```
GET ${WECHAT_API_BASE_URL}/api/public/v1/accountbyurl?url=<encoded-article-url>
```

### 3. Get Article List (需要认证)

```
GET ${WECHAT_API_BASE_URL}/api/public/v1/article?fakeid=<公众号ID>&begin=0&size=5
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| fakeid | Yes | - | Official account ID (from search) |
| begin | No | 0 | Start index |
| size | No | 5 | Number of messages (max 20) |

### 4. Download Article Content (无需认证)

```
GET ${WECHAT_API_BASE_URL}/api/public/v1/download?url=<encoded-article-url>&format=<format>
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| url | Yes | - | Article URL (URL encoded) |
| format | No | html | Output format: `html`, `markdown`, `text` |

### 5. Get Author Info (无需认证)

```
GET ${WECHAT_API_BASE_URL}/api/public/beta/authorinfo?fakeid=<公众号ID>
```

### 6. Get Account Details (需要认证)

```
GET ${WECHAT_API_BASE_URL}/api/public/beta/aboutbiz?fakeid=<公众号ID>
```

## Workflow

### To download a single article:

```bash
# Download article (no auth needed)
curl "$WECHAT_API_BASE_URL/api/public/v1/download?url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('ARTICLE_URL', safe=''))")&format=markdown"
```

### To download articles from an official account:

1. **Search for the account** using keyword or article URL
2. **Get the `fakeid`** from search results
3. **Fetch article list** using the fakeid
4. **Download individual articles** using article URLs

### Example workflow:

```bash
# Step 1: Search for account
curl -H "X-Auth-Key: $WECHAT_API_KEY" \
  "$WECHAT_API_BASE_URL/api/public/v1/account?keyword=%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5&size=1"
# Returns: fakeid = "MjM5MjAxNDM4MA=="

# Step 2: Get article list
curl -H "X-Auth-Key: $WECHAT_API_KEY" \
  "$WECHAT_API_BASE_URL/api/public/v1/article?fakeid=MjM5MjAxNDM4MA==&size=5"
# Returns: list of articles with URLs

# Step 3: Download article (no auth needed)
curl "$WECHAT_API_BASE_URL/api/public/v1/download?url=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FXXXX&format=markdown"
```

## Important Notes

1. **Chinese keywords must be URL encoded** (e.g., `人民日报` → `%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5`)
2. **API key expires** when website login session expires
3. **Download endpoint** works without authentication
4. **Rate limiting** may apply - avoid rapid successive requests

## Response Examples

### Search Account Response
```json
{
  "base_resp": {"ret": 0, "err_msg": "ok"},
  "list": [
    {
      "fakeid": "MjM5MjAxNDM4MA==",
      "nickname": "人民日报",
      "alias": "rmrbwx",
      "signature": "参与、沟通、记录时代。"
    }
  ],
  "total": 1
}
```

### Article List Response
```json
{
  "base_resp": {"ret": 0, "err_msg": "ok"},
  "articles": [
    {
      "title": "文章标题",
      "link": "https://mp.weixin.qq.com/s/XXXXX",
      "cover": "https://...",
      "update_time": 1768025548
    }
  ]
}
```

## Error Handling

| Error | Meaning | Solution |
|-------|---------|----------|
| `认证信息无效` | Invalid auth | Re-login on website, update config.env |
| `invalid session` | Session expired | Re-login on website, update config.env |
| `密钥已过期` | Key expired | Re-login on website, update config.env |

## Verification

Before completing tasks:
1. Confirm API responses are successful (`ret: 0`)
2. Verify downloaded content is not empty
3. Check file format is correct (html/markdown/text)
