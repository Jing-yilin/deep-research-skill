#!/usr/bin/env python3
"""
WeChat Article API utilities.
Handles API requests and TOON format output.
"""

import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional


def _parse_dotenv(path: str) -> dict:
    """Parse key=value pairs from a .env file."""
    result = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                result[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return result


def get_credentials() -> tuple:
    """Load API credentials: os.environ → ~/.zshrc → /opt/data/.env (Docker)."""
    base_url = os.environ.get('WECHAT_API_BASE_URL', '')
    api_key = os.environ.get('WECHAT_API_KEY', '')

    if not base_url:
        result = subprocess.run(
            ['bash', '-c', 'source ~/.zshrc 2>/dev/null; echo "URL:$WECHAT_API_BASE_URL"; echo "KEY:$WECHAT_API_KEY"'],
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('URL:'):
                base_url = line[4:].strip()
            elif line.startswith('KEY:'):
                api_key = line[4:].strip()

    if not base_url:
        env = _parse_dotenv('/opt/data/.env')
        base_url = env.get('WECHAT_API_BASE_URL', '')
        api_key = env.get('WECHAT_API_KEY', '')

    if not base_url:
        raise ValueError("WECHAT_API_BASE_URL not set (checked os.environ, ~/.zshrc, /opt/data/.env)")
    return base_url, api_key


def api_request(endpoint: str, params: Dict[str, str], auth_required: bool = True) -> Dict:
    """Make API request and return JSON response."""
    base_url, api_key = get_credentials()
    
    query = urllib.parse.urlencode(params)
    url = f"{base_url}{endpoint}?{query}"
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    if auth_required and api_key:
        req.add_header('X-Auth-Key', api_key)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {e.reason}"}


def escape_toon_value(value: Any) -> str:
    """Escape value for TOON format (CSV-style in tabular arrays)."""
    if value is None:
        return ""
    s = str(value)
    if ',' in s or '"' in s or '\n' in s:
        return '"' + s.replace('"', '""') + '"'
    return s


def to_toon_tabular(data: List[Dict], fields: List[str]) -> str:
    """Convert list of dicts to TOON tabular format."""
    if not data:
        return ""
    
    rows = []
    for item in data:
        row_values = [escape_toon_value(item.get(f, "")) for f in fields]
        rows.append(",".join(row_values))
    
    return "\n  ".join(rows)


def format_timestamp(ts: int) -> str:
    """Convert Unix timestamp to date string."""
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')


def clean_markdown(content: str) -> str:
    """Clean WeChat article markdown content."""
    # Remove CSS styles at the beginning (everything before first heading or content)
    content = re.sub(r'^[^#!\[]*?(?=!\[|#)', '', content, flags=re.DOTALL)
    
    # Remove inline CSS blocks
    content = re.sub(r'#js_row_immersive.*?}', '', content, flags=re.DOTALL)
    content = re.sub(r'\.sns_opr_btn.*?}', '', content, flags=re.DOTALL)
    content = re.sub(r'img\s*\{[^}]*\}', '', content)
    
    # Remove THUMB STOPPING artifacts
    content = re.sub(r'THUMB\s*\n*STOPPING\s*\n*', '', content)
    
    # Remove javascript void links but keep text
    content = re.sub(r'\[([^\]]+)\]\(javascript:void\\\(0\\\);\)', r'\1', content)
    
    # Remove "在小说阅读器中沉浸阅读" line
    content = re.sub(r'在小说阅读器中沉浸阅读\s*\n*', '', content)
    
    # Remove lines with only whitespace or empty markdown elements
    lines = content.split('\n')
    clean_lines = []
    started = False
    prev_blank = False
    
    for line in lines:
        stripped = line.strip()
        # Skip CSS-like lines
        if stripped.startswith('#js_') or stripped.startswith('img {'):
            continue
        if 'max-width' in stripped and '{' in stripped:
            continue
        # Skip empty lines at the beginning
        if not started and not stripped:
            continue
        started = True
        
        # Collapse multiple blank lines into one
        is_blank = not stripped
        if is_blank and prev_blank:
            continue
        prev_blank = is_blank
        
        clean_lines.append(line.rstrip())
    
    return '\n'.join(clean_lines).strip()
