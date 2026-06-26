#!/usr/bin/env python3
"""
List articles from a WeChat Official Account.
Returns results in TOON format.

Usage:
    python list_articles.py <fakeid> [--limit N]
    
Example:
    python list_articles.py MzkwMDU0MzMyNw== --limit 10
"""

import argparse
import sys
from wechat_api import api_request, to_toon_tabular, format_timestamp


def list_articles(fakeid: str, limit: int = 10) -> str:
    """List articles from account and return TOON formatted results."""
    
    data = api_request(
        '/api/public/v1/article',
        {'fakeid': fakeid, 'size': str(limit)},
        auth_required=True
    )
    
    if 'error' in data:
        return f"error: {data['error']}"
    
    if data.get('base_resp', {}).get('ret') != 0:
        err_msg = data.get('base_resp', {}).get('err_msg', 'Unknown error')
        return f"error: {err_msg}"
    
    articles = data.get('articles', [])
    
    # Build TOON output
    output = []
    output.append(f"fakeid: {fakeid}")
    output.append(f"count: {len(articles)}")
    
    if articles:
        # Extract relevant fields
        clean_articles = []
        for art in articles:
            clean_articles.append({
                'title': art.get('title', ''),
                'date': format_timestamp(art.get('update_time', 0)),
                'author': art.get('author_name', ''),
                'url': art.get('link', ''),
                'digest': art.get('digest', '')[:100] if art.get('digest') else ''
            })
        
        fields = ['title', 'date', 'author', 'url']
        output.append(f"articles[{len(clean_articles)}]{{title,date,author,url}}:")
        output.append(f"  {to_toon_tabular(clean_articles, fields)}")
    else:
        output.append("articles[0]:")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='List articles from WeChat Official Account')
    parser.add_argument('fakeid', help='Account fakeid (from search_account.py)')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Max articles (default: 10)')
    
    args = parser.parse_args()
    
    result = list_articles(args.fakeid, args.limit)
    print(result)


if __name__ == '__main__':
    main()
