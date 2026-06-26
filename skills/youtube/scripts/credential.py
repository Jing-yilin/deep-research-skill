#!/usr/bin/env python3
"""
YouTube credential management.
Reads from environment: YOUTUBE_API_KEY, TRANSCRIPT_API_KEY
"""
import os


def get_youtube_api_key() -> str | None:
    """Get Google YouTube Data API key"""
    return os.environ.get("YOUTUBE_API_KEY")


def get_transcript_api_key() -> str | None:
    """Get TranscriptAPI.com key"""
    return os.environ.get("TRANSCRIPT_API_KEY")


def has_youtube_key() -> bool:
    """Check if YouTube API key is available"""
    return get_youtube_api_key() is not None


def has_transcript_key() -> bool:
    """Check if TranscriptAPI key is available"""
    return get_transcript_api_key() is not None
