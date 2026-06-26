# LinkedIn

Search and retrieve content from LinkedIn via HarvestAPI (read). Post, comment, share URLs, and get stats via Composio (write).

**Read**: `linkedin` CLI (HarvestAPI, `HARVESTAPI_API_KEY`)
**Write**: `uv run python scripts/linkedin_composio.py` (Composio, `COMPOSIO_API_KEY`, user-id: `yilin`)

All commands run from: `/Users/yilin/Developer/DailyTasks/.agents/skills/linkedin`

## Write Operations (Composio)

### Get your profile
```bash
uv run python scripts/linkedin_composio.py get-my-info
```

### Create a text post
```bash
uv run python scripts/linkedin_composio.py create-post --text "Post content here"
uv run python scripts/linkedin_composio.py create-post --text "..." --visibility CONNECTIONS
```
Visibility: `PUBLIC` (default) | `CONNECTIONS` | `LOGGED_IN`

### Create a post with image (3-step auto flow)
```bash
uv run python scripts/linkedin_composio.py create-post-image \
  --file /path/to/image.png \
  --text "Post caption here"
```
Supports jpg, png, gif. Flow: init upload → PUT to LinkedIn → create post with image URN. All handled automatically.

### Share a URL / article
```bash
uv run python scripts/linkedin_composio.py share-url --url "https://..." --title "Optional title" --description "Optional desc"
```

### Comment on a post
```bash
uv run python scripts/linkedin_composio.py comment --post-urn "urn:li:share:12345" --text "Great post!"
```

### Get post content
```bash
uv run python scripts/linkedin_composio.py get-post --post-urn "urn:li:share:12345"
```

### Delete a post
```bash
uv run python scripts/linkedin_composio.py delete-post --share-id "12345"
```

### List reactions on a post
```bash
uv run python scripts/linkedin_composio.py list-reactions --entity-urn "urn:li:share:12345"
```

### Company / org operations
```bash
uv run python scripts/linkedin_composio.py get-company-info
uv run python scripts/linkedin_composio.py get-network-size --org-urn "urn:li:organization:12345"
uv run python scripts/linkedin_composio.py share-stats --org-urn "urn:li:organization:12345"
uv run python scripts/linkedin_composio.py page-stats --org-urn "urn:li:organization:12345"
```

### Image upload (get presigned URL)
```bash
uv run python scripts/linkedin_composio.py init-image-upload
```

All commands: `uv run python scripts/linkedin_composio.py --help`

## Auth Setup

LinkedIn connected via Composio (user_id: `yilin`, auth_config: `ac_2b6X_q-_-NA5`).

```python
# Re-authorize if expired:
from composio import Composio
c = Composio()
resp = c.client.link.create(auth_config_id='ac_2b6X_q-_-NA5', user_id='yilin')
print(resp.redirect_url)
```

## Notes

- Post URNs look like `urn:li:share:7xxxxxxxxxx` or `urn:li:ugcPost:7xxxxxxxxxx`
- Org URNs look like `urn:li:organization:12345`
- Default user-id is `yilin`; override with `--user-id` or `$COMPOSIO_USER_ID`
- All output is TOON-formatted

## CLI Tool: `linkedin`

Rust CLI installed at `~/.local/bin/linkedin`. All output is TOON-formatted for agent consumption.

**Requires**: `HARVESTAPI_API_KEY` environment variable.

```bash
# Profiles
linkedin profile <url-or-username>           # Get profile by URL or username
linkedin profile <target> --email            # Include email lookup
linkedin search-profiles <query>             # Search profiles
linkedin search-profiles <query> --company "Google" --title "Engineer"
linkedin search-profiles <query> --location "San Francisco" --school "Stanford"

# Companies
linkedin company <url-or-name>               # Get company info
linkedin search-companies <query>            # Search companies
linkedin search-companies <query> --size "51-200" --location "NYC"

# Posts
linkedin posts <username>                    # Get profile's posts
linkedin posts <username> --since week       # Filter: 24h, week, month
linkedin company-posts <company-name>        # Get company posts
linkedin post <post-url>                     # Get single post
linkedin search-posts <query>               # Search all posts
linkedin search-posts <query> --author <url> --sort date

# Engagement
linkedin post-comments <post-url>            # Get post comments
linkedin post-reactions <post-url>           # Get post reactions
linkedin profile-comments <username>         # Get profile's comments
linkedin profile-reactions <username>        # Get profile's reactions

# Jobs
linkedin job <url-or-id>                     # Get job details
linkedin search-jobs <query>                 # Search jobs
linkedin search-jobs "ML Engineer" --location "NYC" --workplace remote --salary "140k+"
linkedin search-jobs <query> --experience mid-senior --employment full-time --easy-apply

# Groups & Geo
linkedin group <url-or-id>                   # Get group info
linkedin search-groups <query>               # Search groups
linkedin geo-id <location>                   # Find LinkedIn Geo ID
```

### Build from source

```bash
cd SKILLS_DIR/cli && cargo build --release
cp target/release/linkedin ~/.local/bin/linkedin
```

## API Details

- **Provider**: HarvestAPI (`https://api.harvest-api.com/linkedin`)
- **Auth**: `X-API-Key` header with `HARVESTAPI_API_KEY`
- **Response**: Single items in `data.element`, lists in `data.elements`, pagination in `data.pagination`
- **Data cleaning**: Raw API responses are cleaned to remove noise, keeping only useful fields

## Search Filters Reference

### Job Search
| Filter | Values |
|--------|--------|
| `--workplace` | office, hybrid, remote |
| `--employment` | full-time, part-time, contract, temporary, volunteer, internship |
| `--salary` | 40k+, 60k+, 80k+, 100k+, 120k+, 140k+, 160k+, 180k+, 200k+ |
| `--experience` | internship, entry, associate, mid-senior, director, executive |
| `--since` | 24h, week, month |
| `--sort` | relevance, date |

### Company Search
| Filter | Values |
|--------|--------|
| `--size` | 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+ |

### Common
| Filter | Used by |
|--------|---------|
| `--since` | posts, company-posts, search-posts, search-jobs |
| `--sort` | search-posts, post-comments, search-jobs |
| `--page` | All search/list commands (default: 1) |
