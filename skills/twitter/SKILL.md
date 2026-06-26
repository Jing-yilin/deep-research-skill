---
name: twitter
description: Search and retrieve content from Twitter/X. Get user info, tweets, replies, followers, communities, spaces, and trends via twitterapi.io.
triggers:
  - "twitter"
  - "X"
  - "推特"
  - "tweet"
  - "推文"
---

# Twitter/X Skill

Get user profiles, tweets, replies, followers/following, communities, spaces, and trends from Twitter/X via twitterapi.io.

## Prerequisites

Set API key in `~/.zshrc`:
```bash
export TWITTERAPI_API_KEY="your_api_key"
```

**Quick Check**:
```bash
cd /Users/yilin/Developer/DailyTasks/.agents/skills/twitter
uv run scripts/get_user_info.py elonmusk
```

## Commands

All commands run from: `/Users/yilin/Developer/DailyTasks/.agents/skills/twitter`

### User Endpoints
```bash
python3 scripts/get_user_info.py USERNAME
python3 scripts/get_user_about.py USERNAME
python3 scripts/batch_get_users.py USER_ID1,USER_ID2
python3 scripts/get_user_tweets.py USERNAME --limit 20
python3 scripts/get_user_mentions.py USERNAME --limit 20
python3 scripts/get_followers.py USERNAME --limit 100
python3 scripts/get_following.py USERNAME --limit 100
python3 scripts/get_verified_followers.py USERNAME --limit 20
python3 scripts/check_relationship.py USER1 USER2
python3 scripts/search_users.py "query" --limit 20
```

### Tweet Endpoints
```bash
python3 scripts/get_tweet.py TWEET_ID [TWEET_ID2...]
python3 scripts/search_tweets.py "query" --type Latest --limit 20
python3 scripts/get_tweet_replies.py TWEET_ID --limit 20
python3 scripts/get_tweet_quotes.py TWEET_ID --limit 20
python3 scripts/get_tweet_retweeters.py TWEET_ID --limit 50
python3 scripts/get_tweet_thread.py TWEET_ID
python3 scripts/get_article.py TWEET_ID
```

### List Endpoints
```bash
python3 scripts/get_list_followers.py LIST_ID --limit 20
python3 scripts/get_list_members.py LIST_ID --limit 20
```

### Community Endpoints
```bash
python3 scripts/get_community.py COMMUNITY_ID
python3 scripts/get_community_members.py COMMUNITY_ID --limit 20
python3 scripts/get_community_moderators.py COMMUNITY_ID
python3 scripts/get_community_tweets.py COMMUNITY_ID --limit 20
python3 scripts/search_community_tweets.py "query" --limit 20
```

### Other Endpoints
```bash
python3 scripts/get_space.py SPACE_ID
python3 scripts/get_trends.py --woeid 1  # Worldwide
```

## Search Query Syntax

```bash
# Basic search
python3 scripts/search_tweets.py "AI agent"

# From specific user
python3 scripts/search_tweets.py "from:elonmusk"

# Date range
python3 scripts/search_tweets.py "AI since:2024-01-01 until:2024-12-31"

# Exclude retweets
python3 scripts/search_tweets.py "AI -filter:retweets"

# With media
python3 scripts/search_tweets.py "AI filter:media"

# Minimum engagement
python3 scripts/search_tweets.py "AI min_faves:1000"
```

## API: twitterapi.io
- Base URL: https://api.twitterapi.io/twitter
- Auth: X-API-Key header
- Pricing: ~$0.15-0.18/1k requests
- Docs: https://docs.twitterapi.io/

---

## Advanced: Composio Integration

For **write operations** (tweeting, liking, following, DMs), use `scripts/twitter_composio.py` which requires:
- COMPOSIO_API_KEY environment variable
- Twitter account connected via https://app.composio.dev

### Setup

1. **Set API Key**:
   ```bash
   export COMPOSIO_API_KEY="your_api_key"
   ```

2. **Connect Twitter Account**:
   ```bash
   composio add twitter
   # Opens browser for OAuth authentication
   ```

### Available Write Operations

#### Tweet Operations
```bash
# Create tweet
python3 scripts/twitter_composio.py create-tweet --text "Hello World!"

# Create tweet with media (must upload first)
python3 scripts/twitter_composio.py create-tweet \
  --text "Check this out!" \
  --media 1234567890

# Reply to tweet (for threads)
python3 scripts/twitter_composio.py create-tweet \
  --text "Great point!" \
  --reply-to abc123

# Quote tweet
python3 scripts/twitter_composio.py create-tweet \
  --text "This is interesting!" \
  --quote def456

# Delete tweet
python3 scripts/twitter_composio.py delete-tweet --id abc123
```

#### Engagement Operations
```bash
# Like/Unlike
python3 scripts/twitter_composio.py like --id TWEET_ID
python3 scripts/twitter_composio.py unlike --id TWEET_ID

# Retweet/Unretweet
python3 scripts/twitter_composio.py retweet --id TWEET_ID
python3 scripts/twitter_composio.py unretweet --id TWEET_ID

# Bookmark
python3 scripts/twitter_composio.py add-bookmark --id TWEET_ID
python3 scripts/twitter_composio.py remove-bookmark --id TWEET_ID
```

#### User Operations
```bash
# Follow/Unfollow
python3 scripts/twitter_composio.py follow --username elonmusk
python3 scripts/twitter_composio.py unfollow --username elonmusk

# Block/Unblock
python3 scripts/twitter_composio.py block --username spammer
python3 scripts/twitter_composio.py unblock --username spammer

# Mute/Unmute
python3 scripts/twitter_composio.py mute --username noisy_user
python3 scripts/twitter_composio.py unmute --username noisy_user
```

#### Direct Messages
```bash
# Send DM
python3 scripts/twitter_composio.py send-dm \
  --username recipient \
  --text "Hi there!"
```

#### Media Upload

**Note**: Video upload via Composio API has limitations due to file size restrictions. For videos, consider:
1. Manual upload via Twitter web/mobile interface
2. Use Twitter API v2 directly with tweepy library
3. Upload images (<5MB) works, but video upload actions are currently deprecated in Composio

```bash
# Upload small image (<5MB) - Currently not working (deprecated)
python3 scripts/twitter_composio.py upload-media --file logo.png

# Upload video/GIF or large files - Currently not working (deprecated)
python3 scripts/twitter_composio.py upload-large-media \
  --file video.mp4 \
  --category tweet_video

# Alternative: Post text-only tweets and upload media manually
python3 scripts/twitter_composio.py create-tweet --text "Check out my video!"
```

### Example Workflows

**Post tweet with image:**
```bash
# 1. Upload image
python3 scripts/twitter_composio.py upload-media --file banner.png
# Output: {"data": {"media_id_string": "1234567890", ...}}

# 2. Create tweet with media
python3 scripts/twitter_composio.py create-tweet \
  --text "Check out our latest update! 🚀" \
  --media 1234567890
```

**Create a thread:**
```bash
# 1. Post first tweet
python3 scripts/twitter_composio.py create-tweet \
  --text "1/ Thread about AI agents and their capabilities..."
# Output: {"data": {"id": "abc123", ...}}

# 2. Reply to create thread
python3 scripts/twitter_composio.py create-tweet \
  --text "2/ AI agents can now interact with APIs autonomously..." \
  --reply-to abc123

# 3. Continue thread
python3 scripts/twitter_composio.py create-tweet \
  --text "3/ This opens up new possibilities for automation..." \
  --reply-to def456
```

**Research & engage workflow:**
```bash
# 1. Search for relevant tweets (read-only, use twitterapi.io)
python3 scripts/search_tweets.py "AI agents" --type Latest --limit 10

# 2. Like interesting tweets (write operation, use Composio)
python3 scripts/twitter_composio.py like --id TWEET_ID_1
python3 scripts/twitter_composio.py like --id TWEET_ID_2

# 3. Follow active users (write operation)
python3 scripts/twitter_composio.py follow --username active_user
```

### Important Notes

1. **Character Limits**: 
   - Standard tweets: 280 characters
   - Premium users: Up to 4,000 characters

2. **Media Requirements**:
   - Images: PNG, JPG, GIF (up to 5MB for regular upload)
   - Videos: MP4, MOV (use upload-large-media)
   - Must upload media first to get media_id before tweeting

3. **Rate Limits**:
   - Twitter enforces strict rate limits on write operations
   - Creating too many tweets rapidly may result in temporary restrictions
   - Follow Twitter's automation rules

4. **Thread Creation**:
   - Threads are chains of replies
   - Use --reply-to with the previous tweet ID
   - Each tweet returns an ID for the next reply

5. **Username vs User ID**:
   - Most operations accept username (script converts automatically)
   - Some operations return user IDs in responses

See `scripts/twitter_composio.py --help` for all available commands.
