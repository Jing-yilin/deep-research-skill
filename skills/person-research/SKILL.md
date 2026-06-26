---
name: person-research
description: Research people, teams, and organizations comprehensively. Use when user wants to investigate researchers, founders, teams, companies, or any individual/group's background, including academic profiles, social media presence, work history, publications, and professional networks. Triggers on queries like "调研某人背景", "research this person", "who is behind this project", "team background", "找一下XX的信息".
---

# Person/Team Research Skill

Comprehensive background investigation for individuals, teams, and organizations.

## Research Workflow

1. **Identify targets** - Extract names, affiliations from user query (paper, company, project)
2. **Multi-source search** - Query all available sources in parallel
3. **Cross-reference** - Verify information across sources
4. **Synthesize** - Compile structured profile

## Data Sources (Priority Order)

### Academic/Professional
```bash
# Google Scholar - publications, citations, h-index
WebSearch: "{name} Google Scholar site:scholar.google.com"

# DBLP - computer science publications
WebSearch: "{name} DBLP site:dblp.org"

# OpenReview - ML/AI papers and affiliations
WebSearch: "{name} OpenReview site:openreview.net"

# Semantic Scholar
WebSearch: "{name} site:semanticscholar.org"
```

### Social Media
```bash
# Twitter/X - use twitter skill
cd /Users/yilin/Developer/DailyTasks/.factory/skills/twitter
python3 scripts/search_users.py "{name}" --limit 10
python3 scripts/get_user_info.py {username}
python3 scripts/get_user_tweets.py {username} --limit 20

# LinkedIn - use Harvest API (search profile URL first)
WebSearch: "{name} {affiliation} LinkedIn site:linkedin.com"
curl -s "https://harvest-api.com/linkedin/profile?url={linkedin_url}" \
  -H "x-api-key: $HARVESTAPI_API_KEY"
```

### Enrichment APIs ⭐ High value for founders/executives

```bash
# Hunter.io - verified email finder (58% success, 95-99% confidence)
# Best for: company emails, domain search, email verification
# Strengths: Found Dario Amodei, Guillermo Rauch when PDL failed
curl -s "https://api.hunter.io/v2/email-finder?domain={company_domain}&first_name={first}&last_name={last}&api_key=$HUNTER_API_KEY"

# Domain search - find all emails at a company
curl -s "https://api.hunter.io/v2/domain-search?domain={company_domain}&limit=10&api_key=$HUNTER_API_KEY"

# People Data Labs - social profiles + career history (53% success)
# Best for: LinkedIn/GitHub/Twitter handles, job changes, skills
# Strengths: Found Chelsea Finn's new startup, Logan Kilpatrick's job change
curl -s "https://api.peopledatalabs.com/v5/person/enrich?pretty=true&name={name}&company={company}" \
  -H "X-Api-Key: $PEOPLEDATALABS_API_KEY"

# PDL with LinkedIn URL (more accurate)
curl -s "https://api.peopledatalabs.com/v5/person/enrich?pretty=true&profile=linkedin.com/in/{username}" \
  -H "X-Api-Key: $PEOPLEDATALABS_API_KEY"
```

**API Limitations:**
- Both fail on: academics, Chinese entrepreneurs, very new startups
- Hunter: needs company domain
- PDL: needs name+company or LinkedIn URL

### Startup/Business (for founders, entrepreneurs)
```bash
# Product Hunt - product launches, maker profiles ⭐ High value
WebSearch: "{company} site:producthunt.com"
FetchUrl: https://www.producthunt.com/products/{product-slug}

# Tracxn - funding, valuation, investors ⭐ High value
WebSearch: "{company} Tracxn funding"
WebSearch: "{company} site:tracxn.com"

# Owler - revenue estimates, employee count
WebSearch: "{company} site:owler.com"

# Crunchbase (search via WebSearch, direct access limited)
WebSearch: "{company} Crunchbase funding valuation"

# The Org - org charts, leadership team
WebSearch: "{company} site:theorg.com"
```

### Video/Media
```bash
# YouTube - interviews, talks, demos
cd /Users/yilin/Developer/DailyTasks/.factory/skills/youtube
python3 scripts/search_video.py "{name} {company}" --limit 10
python3 scripts/search_video.py "{name} interview OR talk OR podcast" --limit 5
python3 scripts/get_video_info.py {video_id}

# Podcast appearances
WebSearch: "{name} podcast interview"
```

### Code & Projects
```bash
# GitHub profile/repos
FetchUrl: https://github.com/{username}
FetchUrl: https://github.com/{organization}
WebSearch: "{name} GitHub site:github.com"
```

### General Web
```bash
# Personal homepage
WebSearch: "{name} {affiliation} homepage"

# News/press
WebSearch: "{name} {affiliation}" --category news

# AMiner (Chinese researchers)
WebSearch: "{name} site:aminer.cn"

# GetLatka (SaaS metrics for founders)
WebSearch: "{company} site:getlatka.com"
```

## Output Template

```markdown
## {Person/Team Name} Background Research

### Basic Information
| Field | Info |
|-------|------|
| Current Position | {position} @ {organization} |
| Education | {education} |
| Research Areas | {research_areas} |
| Location | {location} |

### Academic Influence
- [Google Scholar]({google_scholar_url}): {citations} citations, h-index {h_index}
- Notable Works: {notable_papers_with_links}

### Social & Online Presence
- Twitter/X: [@{handle}](https://x.com/{handle}) ({followers} followers)
- GitHub: [{github_username}]({github_url})
- LinkedIn: [{name}]({linkedin_url})
- Personal Homepage: [{domain}]({homepage_url})

### Career Timeline
{timeline_with_links}

### Collaborators & Advisors
{collaborators_with_links}

### Funding & Business (for founders)
- Company: [{company}]({company_url})
- Funding: {funding_status} - [Tracxn]({tracxn_url}) | [Crunchbase]({crunchbase_url})
- Investors: {investors}

### Recent Activities
{recent_activities_with_links}
```

## Parallel Search Strategy

Always run independent searches in parallel to save time:

```
# Good - parallel calls
WebSearch: "{name} Google Scholar"  }
WebSearch: "{name} LinkedIn"        } parallel
WebSearch: "{name} GitHub"          }
twitter search_users.py "{name}"    }

# Then follow up with specific fetches based on results
```

## Tips

- For Chinese names, search both original (张三) and pinyin (Zhang San)
- Check paper affiliations for current employer
- GitHub contribution graphs reveal activity patterns
- Twitter following/followers reveal professional network
- For teams, identify key members first, then research individually
- Product Hunt "Team" tab shows all makers associated with a product
- Tracxn provides more detailed funding data than Crunchbase for many startups
- YouTube "Founders Embassy", "Y Combinator", accelerator channels have founder interviews
- GetLatka has detailed SaaS metrics (ARR, customers, growth) from founder interviews

## When to Use Enrichment APIs

| Scenario | Use Hunter.io | Use PDL |
|----------|---------------|---------|
| Need verified email to contact | ✅ | ❌ |
| Find all contacts at a company | ✅ domain-search | ❌ |
| Get social handles (GitHub/Twitter) | ❌ | ✅ |
| Track job changes | ❌ | ✅ |
| Academic researchers | ❌ | ❌ (use WebSearch) |
| Chinese entrepreneurs | ❌ | ❌ (use AMiner) |
