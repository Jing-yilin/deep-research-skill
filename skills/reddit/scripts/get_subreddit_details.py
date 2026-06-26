#!/usr/bin/env python3
"""
Get rich subreddit details via ScrapeCreators.
Returns weekly_active_users, weekly_contributions, submit_text, icon/header images, etc.
Usage: python3 scripts/get_subreddit_details.py ClaudeAI
"""
import argparse
from toon_format import encode as toon_encode
from scrapecreators_api import sc_get


def main():
    parser = argparse.ArgumentParser(description="Get rich subreddit details (ScrapeCreators)")
    parser.add_argument("subreddit", help="Subreddit name (case-sensitive, e.g. AskReddit)")
    args = parser.parse_args()

    data = sc_get("/v1/reddit/subreddit/details", {"subreddit": args.subreddit})
    print(toon_encode(data))


if __name__ == "__main__":
    main()
