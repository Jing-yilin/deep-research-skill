# WeChat Article Skill - Installation Guide

## Required Dependencies

### 1. Environment Variables (Required)

**Purpose**: API authentication and endpoint configuration

**Check if installed**:
```bash
echo "URL: $WECHAT_API_BASE_URL"
echo "Key: ${WECHAT_API_KEY:0:8}..."
```

**Installation**:

Add to `~/.zshrc`:
```bash
# >>> wechat-article >>>
export WECHAT_API_BASE_URL=<your-deployment-url>  # self-hosted or cloud deployment
export WECHAT_API_KEY=<your-api-key>
# <<< wechat-article <<<
```

Then reload:
```bash
source ~/.zshrc
```

**Get API key**:
1. Visit your deployment URL (self-hosted or cloud)
2. Login via WeChat scan
3. Get `auth-key` from browser cookies

---

### 2. curl (Required)

**No installation required** - curl is available via the Execute tool.

---

## No MCP Required

This skill uses the built-in **Execute** tool to run curl commands. No additional MCP installation is needed.

---

## Configuration Reference

| Variable | Description |
|----------|-------------|
| `WECHAT_API_BASE_URL` | API server URL |
| `WECHAT_API_KEY` | Auth key from browser cookies |

**Note**: API key is tied to website login session. When login expires, get a new key from browser cookies.

---

## Verification

### Test API Connection
```bash
# Test download endpoint (no auth required)
curl "$WECHAT_API_BASE_URL/api/public/v1/download?url=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FGz2TyVkdqg5dOMEa4EHEmw&format=text" | head -100
```

### Test Authenticated Endpoint
```bash
curl -H "X-Auth-Key: $WECHAT_API_KEY" \
  "$WECHAT_API_BASE_URL/api/public/v1/account?keyword=test&size=1"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `认证信息无效` | Re-login on website, update `WECHAT_API_KEY` in ~/.zshrc |
| `invalid session` | Session expired, login again |
| `密钥已过期` | Key expired, get new key from browser cookies |
| Empty response | Check `$WECHAT_API_BASE_URL` is correct |
| Connection refused | Verify deployment is running |

### Debug

```bash
# Check env variables
echo "URL set: $([ -n "$WECHAT_API_BASE_URL" ] && echo 'yes' || echo 'no')"
echo "Key set: $([ -n "$WECHAT_API_KEY" ] && echo 'yes' || echo 'no')"

# Test connectivity
curl -I "$WECHAT_API_BASE_URL"
```

### Update API Key

When key expires:
1. Visit deployment URL
2. Login via WeChat scan
3. Open browser DevTools → Application → Cookies
4. Copy `auth-key` value
5. Update `WECHAT_API_KEY` in `~/.zshrc`
6. Run `source ~/.zshrc`
