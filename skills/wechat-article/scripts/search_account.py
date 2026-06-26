#!/usr/bin/env python3
"""
Search WeChat Official Accounts.
Returns results in TOON format.

Usage:
    python search_account.py <keyword> [--limit N]
    
Example:
    python search_account.py "EPIC Connector" --limit 5
"""

import argparse
import sys
from wechat_api import api_request, to_toon_tabular


def search_account(keyword: str, limit: int = 5) -> str:
    """Search for WeChat accounts and return TOON formatted results."""
    
    data = api_request(
        '/api/public/v1/account',
        {'keyword': keyword, 'size': str(limit)},
        auth_required=True
    )
    
    if 'error' in data:
        return f"error: {data['error']}"
    
    if data.get('base_resp', {}).get('ret') != 0:
        err_msg = data.get('base_resp', {}).get('err_msg', 'Unknown error')
        return f"error: {err_msg}"
    
    accounts = data.get('list', [])
    total = data.get('total', 0)
    
    # Build TOON output
    output = []
    output.append(f"query: {keyword}")
    output.append(f"total: {total}")
    
    if accounts:
        # Extract relevant fields
        clean_accounts = []
        for acc in accounts:
            clean_accounts.append({
                'fakeid': acc.get('fakeid', ''),
                'name': acc.get('nickname', ''),
                'alias': acc.get('alias', ''),
                'bio': acc.get('signature', '')
            })
        
        fields = ['fakeid', 'name', 'alias', 'bio']
        output.append(f"accounts[{len(clean_accounts)}]{{fakeid,name,alias,bio}}:")
        output.append(f"  {to_toon_tabular(clean_accounts, fields)}")
    else:
        output.append("accounts[0]:")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Search WeChat Official Accounts')
    parser.add_argument('keyword', help='Search keyword')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Max results (default: 5)')
    
    args = parser.parse_args()
    
    result = search_account(args.keyword, args.limit)
    print(result)


if __name__ == '__main__':
    main()
