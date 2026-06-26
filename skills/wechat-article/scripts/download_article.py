#!/usr/bin/env python3
"""
Download and clean WeChat article content.
Returns clean markdown/text/html.

Usage:
    python download_article.py <url> [--format FORMAT] [--output FILE]
    
Example:
    python download_article.py "https://mp.weixin.qq.com/s/xxx" --format markdown
    python download_article.py "https://mp.weixin.qq.com/s/xxx" -o article.md
"""

import argparse
import sys
import urllib.parse
import urllib.request
from wechat_api import get_credentials, clean_markdown


def download_article(url: str, fmt: str = 'markdown', output: str = None) -> str:
    """Download article content and return cleaned result."""
    
    base_url, _ = get_credentials()
    
    encoded_url = urllib.parse.quote(url, safe='')
    api_url = f"{base_url}/api/public/v1/download?url={encoded_url}&format={fmt}"
    
    try:
        req = urllib.request.Request(api_url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return f"error: HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"error: Connection error: {e.reason}"
    
    # Clean markdown content
    if fmt == 'markdown':
        content = clean_markdown(content)
    
    # Save to file if specified
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"saved: {output}"
    
    return content


def main():
    parser = argparse.ArgumentParser(description='Download WeChat article')
    parser.add_argument('url', help='Article URL (mp.weixin.qq.com)')
    parser.add_argument('--format', '-f', choices=['markdown', 'text', 'html'], 
                        default='markdown', help='Output format (default: markdown)')
    parser.add_argument('--output', '-o', help='Save to file')
    
    args = parser.parse_args()
    
    result = download_article(args.url, args.format, args.output)
    print(result)


if __name__ == '__main__':
    main()
