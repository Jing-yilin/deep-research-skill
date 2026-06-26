---
name: youtube
description: Search and retrieve content from YouTube. Get video info, transcripts, comments, channel and playlist data.
triggers:
  - "youtube"
  - "YouTube"
  - "视频"
  - "字幕"
  - "transcript"
---

# YouTube Skill

Search videos, get details, transcripts, comments, channel/playlist info from YouTube.

## Prerequisites

Set API keys in `~/.zshrc`:
```bash
export YOUTUBE_API_KEY="your_google_api_key"        # Required
export TRANSCRIPT_API_KEY="your_transcriptapi_key"  # Optional
```

**Quick Check**:
```bash
cd /Users/yilin/Developer/DailyTasks/.factory/skills/youtube
python3 scripts/search_video.py "test" --limit 1
```

## Commands

All commands run from: `/Users/yilin/Developer/DailyTasks/.factory/skills/youtube`

### Search Videos
```bash
python3 scripts/search_video.py "keyword" --limit 10
```

### Get Video Info
```bash
python3 scripts/get_video_info.py VIDEO_ID
python3 scripts/get_video_info.py "https://youtube.com/watch?v=xxx"
```

### Get Transcript
```bash
python3 scripts/get_transcript.py VIDEO_ID
python3 scripts/get_transcript.py VIDEO_ID --metadata
python3 scripts/get_transcript.py VIDEO_ID --format text
```

### Get Comments
```bash
python3 scripts/get_comments.py VIDEO_ID --limit 50
python3 scripts/get_comments.py VIDEO_ID --sort time
```

### Get Channel Info
```bash
python3 scripts/get_channel_info.py CHANNEL_ID
python3 scripts/get_channel_info.py --username USERNAME
```

### Get Playlist
```bash
python3 scripts/get_playlist.py PLAYLIST_ID --limit 50
```

## API Sources

| Feature | API | Auth |
|---------|-----|------|
| Search, Video, Comments, Channel, Playlist | Google YouTube Data API v3 | YOUTUBE_API_KEY |
| Transcripts | transcriptapi.com | TRANSCRIPT_API_KEY |

## URL Formats Supported
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `VIDEO_ID` (raw 11-char ID)
