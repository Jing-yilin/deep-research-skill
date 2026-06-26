---
name: deep-research
description: "Conducts deep research combining web search, Reddit community insights, Twitter/X KOL opinions, WeChat Official Account articles, LinkedIn professional data, government corporate registries, and optional person-research for named individuals. Produces structured reports with social sentiment analysis, official company data, and person profiles. Triggers on: deep research, comprehensive analysis, research report, compare X vs Y, analyze trends, 深度调研, 赛道分析, 人物背景, team background."
---

# Deep Research

Multi-source deep research skill combining web search, Reddit developer communities, Twitter/X industry voices, LinkedIn professional network data, and government corporate registries into a single structured report.

## When to Use

- Market/industry landscape analysis (赛道调研)
- Technology comparison and trend analysis
- Company/product competitive intelligence
- Corporate due diligence — ownership, directors, registration history (→ Worker E auto-added)
- Any topic requiring community sentiment + expert opinion + factual data
- Topics involving named founders, investors, researchers, or executives (→ Worker D auto-added)

## When NOT to Use

- Simple factual lookups (1-2 searches)
- Debugging or code issues
- Tasks with no public discussion

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     DEEP RESEARCH                         │
│                                                           │
│  Phase 1: SCOPE     → Define question & angles            │
│                       + detect named persons              │
│                       + detect company entities            │
│                       + detect Chinese-market relevance   │
│  Phase 2: RETRIEVE  → 3–7 worker subagents IN PARALLEL    │
│    ├─ Worker A: WebSearch     (facts, data, reports)       │
│    ├─ Worker B: Reddit Skill  (community sentiment)       │
│    ├─ Worker C: Twitter Skill (KOL & founder opinions)    │
│    ├─ Worker D: Person Skill  (if persons detected) ─ opt │
│    ├─ Worker E: Corp Registry (if company detected) ─ opt │
│    ├─ Worker F: LinkedIn Skill(company/team intel) ── opt │
│    └─ Worker G: WeChat Skill  (if Chinese topic) ──── opt │
│  Phase 3: ANALYZE   → Cross-reference & synthesize        │
│  Phase 4: REPORT    → Structured output                   │
└──────────────────────────────────────────────────────────┘
```

### Parallel Worker Strategy

Phase 2 uses the `Task` tool with `subagent_type: "worker"` to spawn **3-6 parallel subagents**, each specialized in one data source. All `Task` calls MUST be issued in a **single assistant message** so they execute concurrently.

Each worker returns a structured report. The main agent then merges all 3 results in Phase 3.

---

## Execution Protocol

### Phase 1: SCOPE (1 min)

Define the research question and decompose into angles:

1. **Core question**: What exactly are we researching?
2. **Sub-questions** (3-5): Break into investigatable angles
3. **Data needs**: What facts/numbers/opinions do we need?
4. **Person detection**: Does this topic involve named individuals (founders, investors, researchers, executives)? If yes, list them — Worker D will be added.
5. **Company detection**: Is the topic a specific company, startup, or product with a legal entity? If yes, identify likely jurisdiction — Worker E will be added.
6. **Output format**: Report structure preview

**Person detection signals** (any of these → add Worker D):
- User names specific people ("调研 Scott Wu", "Cognition 的团队背景")
- Topic is a company/startup where founder profiles add context
- KOLs whose background helps interpret their views
- Topic is an investment thesis where LP/GP backgrounds matter

**Company detection signals** (any of these → add Worker E + Worker F):
- Topic is a specific company or startup (e.g., "PagePeek 公司", "调研 Cursor")
- User asks about team, funding, ownership, or corporate structure
- A company website or product domain is mentioned
- Topic involves comparing specific companies

**Worker F (LinkedIn) triggers** — add whenever:
- Topic is a specific company (get employee count, team profiles, company posts)
- Person detection triggered (LinkedIn profiles supplement Twitter/web data)
- User asks about team background, hiring, or company culture
- Worker F is highly complementary with Worker E (registry reveals legal owner; LinkedIn reveals actual team)

**WeChat (Worker G) detection signals** — add whenever:
- Topic is about the Chinese market, a Chinese company, or a Chinese product/brand
- User communicates primarily in Chinese or uses Chinese industry terms (赛道, 融资, 大模型, 新能源, etc.)
- Research involves Chinese KOLs, founders, investors, or policy
- Industry sector with strong Chinese media coverage (AI大模型, 新能源, 消费品, 互联网, 企业服务, 医疗, 教育, etc.)
- User explicitly mentions "公众号" or asks for Chinese media perspective
- Worker G is highly complementary with Workers B/C for Chinese-market topics — Reddit/Twitter have little Chinese-language signal, so WeChat fills that gap

**Jurisdiction inference** for Worker E:
- UK company / London-based / .co.uk domain → UK Companies House
- US company / Delaware / California → SEC EDGAR, state SOS
- EU company → national registries (e.g., Handelsregister DE, Infogreffe FR)
- HK company → ICRIS (Companies Registry)
- Singapore → ACRA BizFile
- If unknown, try UK Companies House first (most accessible), then infer from web research results

Output a brief scope summary before proceeding. Use `TodoWrite` to track phases.

### Phase 2: RETRIEVE (5-15 min)

**CRITICAL: Launch all workers in a SINGLE assistant message so they run concurrently.**

The main agent dispatches 3+ `Task` calls simultaneously. Each worker gets a self-contained prompt with everything it needs — topic, search instructions, output format.

If **person detection** triggered in Phase 1, add **Worker D** to the same batch.
If **company detection** triggered in Phase 1, add **Worker E** (corporate registry) and **Worker F** (LinkedIn) to the same batch.
If **Chinese-market relevance** triggered in Phase 1, add **Worker G** (WeChat articles) to the same batch.

#### Worker A: Web Research

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"Web research: {topic}"`
- `prompt`: see template below

```
Goal: Gather factual data about {topic} from web sources.
Context: This is part of a deep research project. You are the web data worker.

Steps:
1. Run 5-8 WebSearch calls in parallel covering these angles:
   - Market size, revenue, ARR data
   - Funding rounds, valuations
   - Competitive landscape, key companies
   - Technology trends and predictions
   - Challenges, risks, limitations
   - Industry reports (a16z, CB Insights, Gartner)
2. Extract specific numbers, quotes, and data points from search results.
   If a search result snippet contains enough data, use it directly.
   Only use WebSearch — do NOT call FetchUrl (worker may not have it).

Output format (MUST follow exactly):
## Web Research: {topic}

### Key Data Points
- [bullet list of specific facts with source URLs]

### Company/Product Landscape
| Company | Product | Key Metrics | Source |
|---------|---------|-------------|--------|
[table rows]

### Funding & Valuations
| Company | Valuation | Funding | Round | Source |
|---------|-----------|---------|-------|--------|
[table rows]

### Trends & Predictions
- [bullet list with sources]

### Sources
[numbered list of all URLs consulted]
```

#### Worker B: Reddit Research

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"Reddit research: {topic}"`
- `prompt`: see template below

The reddit skill scripts live under the project's `.factory/skills/reddit` directory. Workers should resolve the path relative to the project root.

```
Goal: Gather community sentiment about {topic} from Reddit.
Context: This is part of a deep research project. You are the Reddit sentiment worker.

Tools: Use the reddit skill scripts. Find them by running:
  ls "$(git rev-parse --show-toplevel)"/.factory/skills/reddit/scripts/
Then execute from that directory.

Steps:
1. Search broadly first:
   python3 scripts/search_posts.py "{topic}" --sort top --time year --limit 10
   python3 scripts/search_posts.py "{topic keywords variant}" --sort top --time month --limit 10

2. Search in domain-specific subreddits (pick 2-3 most relevant):
   Subreddit map:
   - AI/ML: MachineLearning, LocalLLaMA, ArtificialInteligence
   - Dev Tools: ExperiencedDevs, programming, webdev
   - AI Coding: ClaudeAI, ChatGPTCoding, cursor
   - Startups: startups, SaaS, technology
   - Investing: wallstreetbets, stocks, investing

   python3 scripts/search_posts.py "{topic}" --subreddit {sub} --sort top --time month --limit 10

3. For posts with score >100, fetch full post + comments:
   python3 scripts/get_post.py {post_id} --comments 15

4. Extract: upvote counts, top comments, personal experience reports, consensus vs controversy.

Output format (MUST follow exactly):
## Reddit Research: {topic}

### High-Signal Discussions
| Post Title | Subreddit | Score | Comments | Core Takeaway |
|------------|-----------|-------|----------|---------------|
[table rows, sorted by score descending]

### Key Community Opinions
- **Consensus views**: [what most upvoted comments agree on]
- **Controversial views**: [minority but notable perspectives]
- **Personal experiences**: [real user reports, not speculation]

### Notable Quotes
> "exact quote" — u/username, {score} points, r/{subreddit}
[3-5 most impactful quotes]

### Sentiment Summary
[1 paragraph: overall community mood — bullish/bearish/mixed, and why]
```

#### Worker C: Twitter/X Research

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"Twitter research: {topic}"`
- `prompt`: see template below

The twitter skill scripts live under the project's `.factory/skills/twitter` directory. Workers should resolve the path relative to the project root.

```
Goal: Gather KOL and industry voice opinions about {topic} from Twitter/X.
Context: This is part of a deep research project. You are the Twitter/X intelligence worker.

Tools: Use the twitter skill scripts. Find them by running:
  ls "$(git rev-parse --show-toplevel)"/.factory/skills/twitter/scripts/
Then execute from that directory.

Steps:
1. Search for top and latest tweets:
   python3 scripts/search_tweets.py "{topic keywords}" --type Top --limit 15
   python3 scripts/search_tweets.py "{topic keywords}" --type Latest --limit 15
   python3 scripts/search_tweets.py "{alternative keywords}" --type Top --limit 10

2. Search specific KOL accounts (pick relevant ones):
   KOL map:
   - AI General: karpathy, ylecun, demabortz
   - AI Coding: aabortz, cursor_ai, cognition
   - VC/Industry: naval, pmarca, paulg, sama
   - Dev Community: swyx, ThePrimeagen, t3dotgg

   python3 scripts/search_tweets.py "from:{handle} {topic}" --type Latest --limit 10

3. For high-engagement tweets (>500 likes), get full details:
   python3 scripts/get_tweet.py {tweet_id}

4. For important threads, get full thread:
   python3 scripts/get_tweet_thread.py {tweet_id}

5. Extract: like/RT counts, view counts, quote tweet takes, reply sentiment.

Output format (MUST follow exactly):
## Twitter Research: {topic}

### Top Voices
| Author | Handle | Tweet Summary | Likes | RTs | Views |
|--------|--------|---------------|-------|-----|-------|
[table rows, sorted by likes descending]

### Key Quotes
> "exact tweet text" — @handle, {likes} likes, {views} views
[5-8 most impactful tweets with full text]

### Industry Signals
- **Bullish signals**: [what KOLs are optimistic about]
- **Bearish signals**: [concerns and criticisms]
- **Breaking news/alpha**: [any novel info not yet in mainstream media]

### Sentiment Summary
[1 paragraph: KOL mood — bullish/bearish/mixed, and why]
```

#### Worker D: Person Research (conditional — only when Phase 1 detected named individuals)

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"Person research: {names}"`
- `prompt`: see template below

Spawn **one Worker D per batch of people** (group up to 5 names in a single worker; spawn multiple workers if more than 5).

```
Goal: Build background profiles for the following people related to {topic}:
  {list of names with roles, e.g. "Scott Wu (CEO, Cognition), Devin's founders"}

Context: This is part of a deep research project. You are the person intelligence worker.

For each person, run these searches IN PARALLEL:

1. Basic identity & career:
   WebSearch: "{name} {company} founder CEO background"
   WebSearch: "{name} LinkedIn site:linkedin.com"
   WebSearch: "{name} {company} Crunchbase OR Tracxn"

2. Academic/research profile (if relevant):
   WebSearch: "{name} Google Scholar OR publications"
   WebSearch: "{name} site:semanticscholar.org OR site:dblp.org"

3. Social presence (use twitter skill scripts at
   "$(git rev-parse --show-toplevel)"/.factory/skills/twitter/scripts/):
   python3 scripts/search_users.py "{name}" --limit 5
   python3 scripts/get_user_info.py {twitter_handle}
   python3 scripts/get_user_tweets.py {twitter_handle} --limit 10

3b. LinkedIn profile (use linkedin CLI at ~/.local/bin/linkedin):
   linkedin search-profiles "{name}"
   linkedin profile {username}
   → Extract: experience history, education, skills, connections count, open_to_work

4. Media & talks:
   WebSearch: "{name} interview podcast OR talk OR keynote"
   WebSearch: "{name} {company} news 2025 2026"

5. For founders, add company signals:
   WebSearch: "{company} funding valuation investors"
   WebSearch: "{company} revenue ARR customers"

Output format (MUST follow exactly):
## Person Research: {topic}

### {Person Name 1} — {Role}
| Field | Info |
|-------|------|
| Current role | {title} @ {org} |
| Background | {education / previous companies} |
| Twitter/X | @{handle} ({followers} followers) |
| GitHub | {github if available} |
| LinkedIn | {linkedin url if found} |

**Career highlights**: [3-5 bullets with sources]

**Public stance on {topic}**: [what they've said publicly, with tweet/article links]

**Reputation signal**: [how community views them — credible/controversial/trusted]

---

### {Person Name 2} — {Role}
[same structure]

### Cross-Person Insights
- **Network connections**: [who knows who, co-investors, co-founders, shared advisors]
- **Alignment/conflict**: [do their public views align or conflict on key questions?]
- **Trust signals**: [track record, notable wins/failures]
```

#### Worker E: Corporate Registry Research (conditional — only when Phase 1 detected a company entity)

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"Corporate registry: {company}"`
- `prompt`: see template below

This worker queries **government corporate registries** — publicly available, authoritative data that reveals ownership, directors, registered addresses, filing history, and related entities that are often invisible on social media and marketing channels.

```
Goal: Look up official corporate registration data for {company} from government registries.
Context: This is part of a deep research project. You are the corporate registry intelligence worker.
The company appears to be based in {jurisdiction_hint}.

Steps (adapt based on jurisdiction):

=== UK Companies House (most accessible, try first if jurisdiction unclear) ===
1. Search for the company:
   WebSearch: "{company_name} site:find-and-update.company-information.service.gov.uk"
   WebSearch: "{company_name} Companies House UK registration"

2. If found, use FetchUrl to scrape these pages (replace {company_number}):
   - Overview: https://find-and-update.company-information.service.gov.uk/company/{company_number}
   - Officers: https://find-and-update.company-information.service.gov.uk/company/{company_number}/officers
   - PSC (Persons with Significant Control): https://find-and-update.company-information.service.gov.uk/company/{company_number}/persons-with-significant-control
   - Filing history: https://find-and-update.company-information.service.gov.uk/company/{company_number}/filing-history

3. For each director found, check their OTHER appointments:
   FetchUrl the officer's appointments page (linked from the officers page)
   This reveals their full company portfolio — critical for pattern detection.

4. Check the registered address — is it a virtual office / registration agent?
   WebSearch: "{registered_address}" to see how many other companies share it.

=== US (SEC EDGAR / State SOS) ===
1. SEC EDGAR (for larger companies):
   WebSearch: "{company_name} site:sec.gov EDGAR"
   WebSearch: "{company_name} SEC filing 10-K OR S-1"

2. Delaware Division of Corporations:
   WebSearch: "{company_name} site:icis.corp.delaware.gov"
   WebSearch: "{company_name} Delaware corporation registration"

3. California SOS:
   WebSearch: "{company_name} site:bizfileonline.sos.ca.gov"

=== Other Jurisdictions ===
- Hong Kong ICRIS: WebSearch "{company_name} site:icris.cr.gov.hk"
- Singapore ACRA: WebSearch "{company_name} ACRA BizFile Singapore"
- Germany Handelsregister: WebSearch "{company_name} site:handelsregister.de"
- France Infogreffe: WebSearch "{company_name} site:infogreffe.fr"
- Crunchbase/Tracxn as fallback: WebSearch "{company_name} site:crunchbase.com OR site:tracxn.com"

=== Cross-check ===
5. Search for related/sister companies by the same directors:
   WebSearch: "{director_name} director companies house" (UK)
   WebSearch: "{director_name} officer SEC EDGAR" (US)

6. Verify registered address patterns:
   WebSearch: "{full_registered_address}" — count co-registered companies

Output format (MUST follow exactly):
## Corporate Registry Research: {company}

### Company Registration
| Field | Info |
|-------|------|
| Legal name | {full legal name} |
| Registration number | {number} |
| Jurisdiction | {country / state} |
| Incorporated on | {date} |
| Status | {active / dissolved / etc.} |
| Registered address | {full address} |
| Company type | {Ltd / Inc / LLC / etc.} |
| Share capital | {if available} |
| SIC / Industry codes | {codes and descriptions} |
| Registry URL | {direct link to government page} |

### Directors & Officers
| Name | Role | Appointed | Nationality | DOB (month/year) |
|------|------|-----------|-------------|-------------------|
[table rows]

### Persons with Significant Control (Ownership)
| Name | Control type | Shareholding | Notified on |
|------|-------------|--------------|-------------|
[table rows — UK PSC or equivalent ownership data]

### Filing History (key filings only)
| Date | Type | Description |
|------|------|-------------|
[table rows — incorporation, accounts, significant changes]

### Director's Other Companies
| Director | Company | Registration # | Incorporated | Status | Same address? |
|----------|---------|----------------|--------------|--------|---------------|
[table rows — reveals the director's full company portfolio]

### Registered Address Analysis
- Address type: [real office / virtual office / registration agent]
- Other companies at same address: [count and notable names]
- Signal: [legitimate business address vs. mass-registration address]

### Key Findings
- [bullet list of notable patterns: single-person company, shell indicators, rapid incorporation, shared addresses, etc.]

### Sources
[numbered list of all registry URLs and search URLs consulted]
```

#### Worker F: LinkedIn Research (conditional — when company or persons detected)

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"LinkedIn research: {company/topic}"`
- `prompt`: see template below

This worker uses the `linkedin` CLI (`~/.local/bin/linkedin`) backed by HarvestAPI. It reveals **team composition, employee backgrounds, company metrics, and professional network signals** that are invisible on Twitter/Reddit/web.

**Why LinkedIn matters**: LinkedIn is the single best source for team intelligence — it reveals actual employees (not just founders), their real work history, education, tenure, and whether they've already left. Combined with Worker E (corporate registry), it exposes the gap between marketing narrative and operational reality.

```
Goal: Gather professional network intelligence about {company/topic} from LinkedIn.
Context: This is part of a deep research project. You are the LinkedIn intelligence worker.

Tools: Use the linkedin CLI at ~/.local/bin/linkedin. It requires HARVESTAPI_API_KEY (already configured).

Steps:

=== Company Intelligence ===
1. Get company profile:
   linkedin company {company_name_or_url}
   → Extract: employee_count, followers, description, website

2. Search for company (if direct lookup fails):
   linkedin search-companies "{company_name}"

=== Team Discovery ===
3. Search for people associated with the company:
   linkedin search-profiles "{company_name}"
   linkedin search-profiles "{company_name}" --page 2
   → This reveals ALL employees who list the company on LinkedIn, not just founders

4. For each key person found (founders, C-suite, senior staff), get full profile:
   linkedin profile {username}
   → Extract: experience (with dates!), education, skills, connections count, open_to_work status

5. Critical signals to extract per person:
   - Current vs. past employment at the company (have they LEFT?)
   - Employment duration and overlap with other team members
   - Education background — does it match the company's domain?
   - connections count — <50 suggests inactive/new LinkedIn user
   - open_to_work: true — suggests they may be leaving/have left
   - Premium/verified status

=== Company Content ===
6. Get company posts (optional, if time allows):
   linkedin company-posts {company_name} --since month
   → Extract: post frequency, engagement levels, content themes

7. Search for posts mentioning the company:
   linkedin search-posts "{company_name}"
   → Extract: external mentions, sentiment

=== Person Research Supplement (when Worker D also runs) ===
8. For specific named individuals:
   linkedin profile {username_or_url}
   → Provides structured career data that WebSearch often misses

Output format (MUST follow exactly):
## LinkedIn Research: {company/topic}

### Company Profile
| Field | Info |
|-------|------|
| Name | {name} |
| LinkedIn URL | {url} |
| Website | {website} |
| Employee count | {employee_count} (LinkedIn-reported) |
| Followers | {followers} |
| Description | {first 200 chars} |

### Team Roster (from LinkedIn search)
| Name | Role/Headline | Location | Status | LinkedIn |
|------|---------------|----------|--------|----------|
[table rows — sorted by seniority/relevance]

Status values: Current, Left (with date), Open to Work, Unknown

### Key Person Profiles
For each important team member:

#### {Name} — {Role}
| Field | Info |
|-------|------|
| LinkedIn | {url} |
| Location | {location} |
| Connections | {count} |
| Education | {school, degree, field} |
| At {company} | {start_date} → {end_date or Present} ({duration}) |
| Previous | {notable prior employers} |
| Open to work | {yes/no} |
| Skills | {top 5 relevant skills} |

### Team Analysis
- **Team size**: LinkedIn-reported {N} vs. team profiles found {M}
- **Turnover signals**: [who has left, who is open to work]
- **Education pattern**: [common schools, degrees — reveals recruiting pipeline]
- **Location distribution**: [all London? remote? China-based?]
- **Seniority gaps**: [is there a CTO? any senior engineers? or all junior/marketing?]
- **Domain expertise**: [do team skills match the product domain?]

### LinkedIn vs. Marketing Comparison
- Company website claims: {what the website says about team}
- LinkedIn reality: {what LinkedIn data shows}
- Discrepancies: [hidden founder, inflated team size, departed employees still shown, etc.]

### Sources
[list of all linkedin CLI commands run and key URLs]
```

#### Worker G: WeChat Official Account Research (conditional — when Phase 1 detected Chinese-market relevance)

Issue via `Task` tool:
- `subagent_type`: `"worker"`
- `description`: `"WeChat research: {topic}"`
- `prompt`: see template below

This worker reads **WeChat Official Account (微信公众号) articles** — the primary long-form media channel for Chinese B2B and B2C audiences. It surfaces industry analysis, company announcements, investor takes, and expert commentary that is invisible on Western platforms.

The wxa CLI lives under the project's `.claude/skills/wechat-article/cli/target/release/wxa`. Workers should resolve the path relative to the project root.

```
Goal: Gather WeChat Official Account article intelligence about {topic}.
Context: This is part of a deep research project. You are the WeChat media worker.

Tools: Use the wxa CLI. Resolve the binary path:
  WXA="$(git rev-parse --show-toplevel)/.claude/skills/wechat-article/cli/target/release/wxa"

Fallback to Python scripts if binary unavailable:
  SCRIPTS="$(git rev-parse --show-toplevel)/.claude/skills/wechat-article/scripts"

Steps:

1. Identify 4-6 relevant WeChat accounts for this topic.
   Pick accounts matching the topic domain:
   - AI/大模型: 机器之心, 量子位, 新智元, 硅星人, AI范儿
   - VC/创投: 36氪, 创业邦, 投中网, 华兴资本
   - 互联网/科技: 虎嗅网, 极客公园, 钛媒体
   - 新能源/汽车: 电动星球News, 晚点Auto
   - 企业服务/SaaS: ToB行业头条, SaaS白夜行
   - Use topic-specific names if the above don't match

2. Search for each account:
   $WXA search "{account_name}" --limit 3

   Or Python: python3 $SCRIPTS/search_account.py "{account_name}" --limit 3

   Save the `fakeid` for each matched account.

3. List recent articles from each account (get last 10):
   $WXA list {fakeid} --limit 10

   Or Python: python3 $SCRIPTS/list_articles.py {fakeid} --limit 10

4. From the article list, pick 3-5 most relevant articles per account
   based on title relevance to the research topic.
   Avoid articles older than 6 months unless the topic is historical.

5. Download selected articles in markdown format:
   $WXA download "{article_url}" --format markdown

   Or Python: python3 $SCRIPTS/download_article.py "{article_url}" --format markdown

   Download 8-15 articles total across all accounts.

6. Extract from downloaded articles:
   - Key data points: market size, funding, company metrics, adoption numbers
   - Expert opinions and analysis
   - Company announcements and product launches
   - Policy signals and regulatory context
   - Author name and publication date for attribution

Output format (MUST follow exactly):
## WeChat Research: {topic}

### Accounts Surveyed
| 公众号名称 | Fakeid | 文章总数 | 备注 |
|-----------|--------|----------|------|
[table rows]

### Key Articles & Insights
| 标题 | 公众号 | 日期 | 核心观点 | 文章链接 |
|------|--------|------|----------|----------|
[table rows, sorted by date descending, 8-15 rows]

### Key Data Points
- [bullet list of specific facts, numbers, quotes with article source attribution]

### Expert & Industry Opinions
- **看多观点 (Bullish)**: [what Chinese analysts/KOLs are optimistic about]
- **看空/质疑观点 (Bearish/skeptical)**: [concerns, risks, criticisms from Chinese media]
- **政策信号 (Policy signals)**: [any regulatory or government-related commentary]

### Notable Quotes
> "exact quote" — 作者/账号, 文章标题, YYYY-MM-DD
[3-5 most impactful quotes]

### Sentiment Summary
[1 paragraph: Chinese media mood on this topic — optimistic/pessimistic/neutral, dominant narrative vs. minority views]

### Sources
[numbered list of all article URLs downloaded]
```

#### Fallback: Direct Execution

If worker subagents are unavailable or fail, fall back to running the searches directly from the main agent using the same tool commands listed above. Prioritize: WebSearch first, then LinkedIn, then Reddit, then Twitter, then WeChat. For person research, invoke the `/person-research` skill directly. For corporate registry, the main agent should run the WebSearch + FetchUrl queries from Worker E's template directly. For LinkedIn, run the `linkedin` CLI commands from Worker F's template directly. For WeChat, run the `wxa` CLI commands from Worker G's template directly using `$(git rev-parse --show-toplevel)/.claude/skills/wechat-article/cli/target/release/wxa`.

### Phase 3: ANALYZE (3-5 min)

**Input: Merge all worker reports returned from Phase 2 (3-5 workers).**

#### 3A: Cross-Reference

For each major claim, check if it's supported by:
- [ ] Worker A (web data — factual basis)
- [ ] Worker B (Reddit — community validation)
- [ ] Worker C (Twitter — expert/KOL alignment)
- [ ] Worker D (person profiles — if spawned)
- [ ] Worker E (corporate registry — if spawned)
- [ ] Worker F (LinkedIn — if spawned)
- [ ] Worker G (WeChat articles — if spawned)

Flag contradictions between sources. These are the most interesting findings.

**Person–Topic connection** (when Worker D ran): link each person's background to the main topic findings. E.g., a founder's academic background explains their technical approach; an investor's track record calibrates their bullish view.

**Registry–Marketing contradiction** (when Worker E ran): compare official registry data against the company's public marketing. Key signals:
- Directors listed in registry vs. team shown on website — are there hidden founders?
- Registered address vs. claimed office — virtual office suggests smaller operation than marketed
- Incorporation date vs. claimed founding date — discrepancies suggest narrative crafting
- Share capital vs. claimed fundraising — GBP 100 capital with "Series A" claims = red flag
- Director's other companies — serial shell registration pattern vs. legitimate portfolio

**LinkedIn–Reality triangulation** (when Worker F ran): LinkedIn is the strongest signal for team truth.
- Registry director vs. LinkedIn team — does the legal owner even appear on the company's LinkedIn?
- Employee count (LinkedIn) vs. claimed team size — inflation or deflation?
- Departed employees — LinkedIn shows end dates; company website may still list them
- open_to_work signals — team members seeking new roles = instability indicator
- Education/skills vs. product domain — fashion school background at an AI company = mismatch
- Connections count — <50 connections on key team members = low professional credibility
- Worker E + F combined: registry reveals the legal puppet master; LinkedIn reveals the actual crew

#### 3B: Sentiment Matrix

Build a sentiment view:
```
                Web Data    Reddit     Twitter    WeChat (if G ran)
Topic A:        Bullish     Skeptical  Mixed      Bullish           → EAST/WEST DIVERGENCE
Topic B:        Neutral     Positive   Positive   Positive          → CONSENSUS
Topic C:        Negative    Negative   Negative   Negative          → STRONG SIGNAL
```

**WeChat–Western media triangulation** (when Worker G ran):
- Chinese media sentiment vs. Western media/Reddit/Twitter on the same topic
- WeChat-only signals: policy context, Chinese market adoption data, local KOL takes
- Divergences between Chinese and Western narratives = the most strategically interesting findings

#### 3C: Synthesize

- Identify patterns across sources
- Find non-obvious connections
- Generate original insights (not just summarizing)
- Note confidence levels per finding

### Phase 4: REPORT (5-10 min)

Generate the report to `.archive/reports/YYYY-MM-DD/{topic-slug}.md` with Obsidian-compatible format:

```markdown
---
aliases: ["{Topic short name}"]
tags: [deep-research, {relevant-tags}]
date: YYYY-MM-DD
sources: [web, reddit, twitter]
---

# {Topic} 深度调研报告

> 调研日期: YYYY-MM-DD
> 数据源: Web Search + Reddit + Twitter/X [+ Corporate Registry] [+ Person Research]

## Executive Summary
[3-5 bullet points, 200-300 words]

## 一、{Main Section 1}
[Findings with inline citations]

## 二、{Main Section 2}
[Continue sections as needed]

## N、社交媒体舆情分析

### Reddit 社区声音
| 帖子/讨论 | 社区 | 热度 | 核心观点 |
|-----------|------|------|----------|
[Table of key Reddit discussions with scores and summaries]

### Twitter/X 行业声音
| 发言人 | 影响力 | 观点 |
|--------|--------|------|
[Table of key tweets with engagement metrics]

### 微信公众号声音（仅当 Worker G 运行时）
| 公众号 | 文章标题 | 日期 | 核心观点 |
|--------|----------|------|----------|
[Table of key WeChat articles with summaries]

### 多空分歧
[Where sources agree and disagree]

### 中西方叙事对比（仅当 Worker G 运行时）
[Compare Chinese media (WeChat) vs. Western media (Reddit/Twitter/web) narratives — divergences are the most strategically valuable findings]

## N+1、公司注册信息（仅当 Worker E 运行时）

[Official corporate registration data from government registry]

| 字段 | 信息 |
|------|------|
| 法定名称 | {legal name} |
| 注册编号 | {number} |
| 注册地 | {jurisdiction} |
| 成立日期 | {date} |
| 注册地址 | {address} (真实办公/虚拟地址) |
| 注册资本 | {share capital} |
| 状态 | {active/dissolved} |

### 董事与实际控制人
| 姓名 | 角色 | 国籍 | 持股比例 | 其他名下公司数 |
|------|------|------|----------|----------------|
[table rows]

### 注册信息 vs 公开营销对比
[Contradictions or confirmations between registry data and marketing claims]

## N+2、团队与LinkedIn情报（仅当 Worker F 运行时）

### 公司 LinkedIn 概况
| 字段 | 信息 |
|------|------|
| LinkedIn 员工数 | {employee_count} |
| 关注者 | {followers} |
| LinkedIn URL | {url} |

### 团队名单
| 姓名 | 角色 | 在职状态 | 教育背景 | 来源 |
|------|------|----------|----------|------|
[table rows from Worker F — current, departed, open_to_work]

### 团队分析
- **实际团队规模**: LinkedIn 报告 {N} 人 vs 网站声称 {M} 人
- **人员流动**: [谁已离开、谁在找工作]
- **背景匹配度**: [团队技能/教育是否匹配产品方向]
- **注册人 vs LinkedIn**: [Companies House 董事是否出现在 LinkedIn 团队中]

## N+3、关键人物背景（仅当 Worker D 运行时）

[For each researched person: role, background summary, public stance on topic, community reputation]

| 人物 | 角色 | 背景亮点 | 对本赛道的公开观点 | 可信度信号 |
|------|------|----------|-------------------|------------|
[table rows from Worker D output]

### 人物关系网络
[Connections, shared investors, co-founders, advisors — if found]

## 趋势预判
[Forward-looking analysis with confidence levels]

## 参考来源
[All sources: web URLs, Reddit post links, Tweet IDs]
```

After generating the report, offer to:
- Upload to GitHub Gist (`gh gist create`)
- Archive via `/archive` skill (only when user explicitly requests)

### Obsidian Wikilink Convention

When referencing reports from other `.archive/` files, use Obsidian `[[wikilinks]]`:
- Link to a report: `[[dan-koe-growth-trajectory]]` (filename without `.md`)
- Link with alias: `[[dan-koe-growth-trajectory|Dan Koe 调研]]`
- Reports live in `.archive/reports/YYYY-MM-DD/{slug}.md`
- Archive entries in `.archive/YYYY-MM-DD/` can reference reports with `[[slug]]`
- The `aliases` field in frontmatter enables Obsidian search by short name

---

## Quality Standards

- **Minimum sources**: 10+ web, 5+ Reddit posts, 5+ tweets
- **Citation**: Every factual claim must have a source
- **Balance**: Include both bullish and bearish views
- **Recency**: Prioritize last 6 months of data
- **Specificity**: Use exact numbers, not "significant growth"
- **Reddit signals**: Posts with >100 upvotes = meaningful signal
- **Twitter signals**: Tweets with >100 likes from verified/notable accounts = meaningful
- **Corporate registry**: Government data is highest-authority source — always trumps marketing claims when contradictions arise
- **LinkedIn**: Professional profiles with employment dates are second-highest authority for team data — people rarely fake LinkedIn work history. Key signals: employee_count, departed staff, open_to_work, education mismatch, connections count
- **WeChat articles**: For Chinese-market topics, WeChat is the primary long-form media channel — aim for 8+ articles from 3+ accounts. WeChat-only signals (policy, Chinese market data, local sentiment) should be surfaced explicitly when they differ from Western sources

## Language

- Default to user's language (Chinese if user speaks Chinese)
- Technical terms keep English originals (e.g., ARR, CAGR, SWE)
- Bilingual for key quotes from English sources

---

## Example Invocation

User: "深度调研软件工厂赛道"

**Phase 1 — SCOPE:**
Core question: AI Software Engineering market landscape
Sub-questions: market size, key players, tech routes, sentiment, trends

**Phase 2 — RETRIEVE (4 workers dispatched in one message, persons detected):**

```xml
<Task subagent_type="worker" description="Web research: AI coding">
  <prompt>[full web worker prompt]</prompt>
</Task>

<Task subagent_type="worker" description="Reddit research: AI coding">
  <prompt>[full reddit worker prompt]</prompt>
</Task>

<Task subagent_type="worker" description="Twitter research: AI coding">
  <prompt>[full twitter worker prompt]</prompt>
</Task>

<!-- Worker D added because Phase 1 detected: Scott Wu (CEO), Russell Kaplan (CTO) -->
<Task subagent_type="worker" description="Person research: Scott Wu, Russell Kaplan">
  <prompt>[full person worker prompt with names and roles filled in]</prompt>
</Task>
```

Worker A returns: funding tables, market data, company landscape
Worker B returns: r/ExperiencedDevs sentiment, r/ClaudeAI discussions
Worker C returns: @karpathy, @naval tweets, KOL opinion matrix
Worker D returns: Scott Wu / Russell Kaplan profiles, career history, public stance, network

**Phase 3 — ANALYZE:**
Merge 3 worker reports, cross-reference, build sentiment matrix

**Phase 4 — REPORT:**
Structured report with social sentiment chapter → `.archive/reports/YYYY-MM-DD/{topic}.md`
