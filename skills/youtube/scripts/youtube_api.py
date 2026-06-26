#!/usr/bin/env python3
"""
YouTube API wrapper using only stdlib.
Supports Google YouTube Data API v3 and TranscriptAPI.com
"""
import urllib.request
import urllib.parse
import json
import re
import sys
from credential import get_youtube_api_key, get_transcript_api_key

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
TRANSCRIPT_API_BASE = "https://transcriptapi.com/api/v2"


def api_request(url: str, headers: dict = None) -> dict:
    """Make HTTP GET request and return JSON"""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"error: HTTP {e.code} - {error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def parse_video_id(url_or_id: str) -> str:
    """Extract video ID from URL or return as-is if already an ID"""
    if len(url_or_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', url_or_id):
        return url_or_id
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def format_duration(iso_duration: str) -> str:
    """Convert ISO 8601 duration (PT1H2M3S) to human readable (1:02:03)"""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if not match:
        return iso_duration
    h, m, s = match.groups()
    h, m, s = int(h or 0), int(m or 0), int(s or 0)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_count(num: int | str) -> str:
    """Format large numbers (1234567 -> 1.2M)"""
    n = int(num) if isinstance(num, str) else num
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def youtube_api(endpoint: str, params: dict) -> dict:
    """Call Google YouTube Data API"""
    api_key = get_youtube_api_key()
    if not api_key:
        print("error: YOUTUBE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    params["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    return api_request(url)


def transcript_api(video_id: str, format: str = "json", 
                   include_timestamp: bool = True, 
                   send_metadata: bool = False) -> dict:
    """Call TranscriptAPI.com"""
    api_key = get_transcript_api_key()
    if not api_key:
        print("error: TRANSCRIPT_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    params = {
        "video_url": video_id,
        "format": format,
        "include_timestamp": str(include_timestamp).lower(),
        "send_metadata": str(send_metadata).lower(),
    }
    url = f"{TRANSCRIPT_API_BASE}/youtube/transcript?{urllib.parse.urlencode(params)}"
    headers = {"Authorization": f"Bearer {api_key}"}
    return api_request(url, headers)
