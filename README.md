# deep-research skill (+ dependencies)

A self-contained bundle of the **`/deep-research`** agent skill and every skill it
depends on. `deep-research` runs a multi-source investigation — web search, Reddit
community sentiment, Twitter/X KOL opinion, LinkedIn team intelligence, government
corporate registries, WeChat (微信公众号) media, and optional person profiles — then
fan-out merges everything into one structured report.

> 这是 `/deep-research` 这个 skill 的完整打包，包含它运行时会调用的所有依赖 skill。
> 下面列出了需要哪些 API key 以及从哪里获取。

## What's in here

```
skills/
├── deep-research/      ← the main skill (orchestrator, no API key of its own)
├── reddit/             ← Worker B: community sentiment (public API; key optional)
├── twitter/            ← Worker C: KOL / founder opinions      [needs key]
├── linkedin/           ← Worker F: team intel (Rust CLI)       [needs key]
├── wechat-article/     ← Worker G: Chinese media (Rust CLI)    [needs key]
├── person-research/    ← Worker D: named-person background profiles
├── youtube/            ← used by person-research (optional)
└── scrapecreators-api/ ← Reddit enhanced sorts + generic social scraping
```

The orchestrator itself (`deep-research`) calls **no API directly** — it spawns
worker subagents that each drive one of the dependency skills, plus the agent
harness's built-in `WebSearch` (Worker A). So the keys you need depend on which
workers you want active.

## Required API keys & where to get them

Copy `.env.example` → `.env` and fill in the keys for the workers you want. Each
key is read from the environment by the relevant skill's scripts/CLI.

| Env var | Powers | Required? | Get it at |
|---|---|---|---|
| `TWITTERAPI_API_KEY` | Twitter/X (Worker C) + person-research social lookup | **Required** for the Twitter worker | https://twitterapi.io |
| `HARVESTAPI_API_KEY` | LinkedIn `linkedin` CLI (Worker F) + person profiles | **Required** for the LinkedIn worker | https://harvest-api.com |
| `WECHAT_API_BASE_URL` + `WECHAT_API_KEY` | WeChat 公众号 articles (Worker G) | **Required** for the WeChat worker | self-hosted backend — see [WeChat note](#wechat-worker-g--self-hosted) |
| `SCRAPECREATORS_API_KEY` | Reddit `--sort comment_count`/`best`, and the `scrapecreators-api` skill | Optional (basic Reddit search works without it) | https://scrapecreators.com |
| `YOUTUBE_API_KEY` | YouTube lookups inside person-research | Optional | Google Cloud Console → enable **YouTube Data API v3** |
| `TRANSCRIPT_API_KEY` | YouTube transcripts | Optional | https://www.transcriptapi.com |
| `HUNTER_API_KEY` | person-research email enrichment | Optional | https://hunter.io |
| `PEOPLEDATALABS_API_KEY` | person-research career/social enrichment | Optional | https://peopledatalabs.com |
| `COMPOSIO_API_KEY` | LinkedIn/Reddit/Twitter **write** ops only | Optional (deep-research is read-only) | https://composio.dev |

**No key needed:** Reddit basic read (public JSON API), and Worker A's web search
(provided by your agent harness, e.g. Claude Code's `WebSearch` tool).

### Minimum viable setup

You don't need every key. The skill auto-skips a worker if its topic doesn't call
for it, and degrades gracefully if a key is missing:

- **Just web + Reddit**: no keys at all (Worker A + basic Reddit).
- **+ Twitter sentiment**: add `TWITTERAPI_API_KEY`.
- **+ Team/company due diligence**: add `HARVESTAPI_API_KEY` (LinkedIn).
- **+ Chinese-market topics**: stand up the WeChat backend and set the two `WECHAT_*` vars.

## Runtime prerequisites

- **Python ≥ 3.12** with [`uv`](https://github.com/astral-sh/uv). All Python skills
  (reddit, twitter, linkedin scripts, wechat-article, youtube) share **one** uv
  environment defined by the root `pyproject.toml` — run `uv sync` once at the repo
  root. Third-party deps are just `composio`, `requests`, and `toon_format`; everything
  else each script imports is the stdlib or a local sibling module.
- **Rust / `cargo`** to build the two CLIs (`linkedin`, `wxa`). Prebuilt binaries and
  venvs are intentionally **not** committed — build them locally (below).

## Install

> For a deterministic, step-by-step setup (agent-followable, with per-step verify
> commands and troubleshooting), see **[INSTALL.md](./INSTALL.md)**. Quick version below.

1. **Clone & configure keys**
   ```bash
   git clone <this-repo> deep-research-skill && cd deep-research-skill
   cp .env.example .env       # fill in the keys you need
   set -a; source .env; set +a   # or add the exports to ~/.zshrc
   ```

2. **Create the single shared Python environment** (covers every Python skill)
   ```bash
   uv sync                 # at the repo root — creates ./.venv with all deps
   source .venv/bin/activate
   ```
   Then run any skill script against that venv, e.g.
   `python3 skills/reddit/scripts/search_posts.py "claude code" --limit 5`.
   (Scripts add their own `scripts/` dir to `sys.path`, so their local sibling
   imports work regardless of where you launch them.)

3. **Build the LinkedIn CLI** → `linkedin` (Worker F)
   ```bash
   cd skills/linkedin/cli && cargo build --release
   cp target/release/linkedin ~/.local/bin/linkedin   # the skill expects it on PATH here
   ```

4. **Build the WeChat CLI** → `wxa` (Worker G)
   ```bash
   cd skills/wechat-article/cli && cargo build --release
   # binary lands at skills/wechat-article/cli/target/release/wxa
   ```

5. **Register the skills with your agent.** Point your harness's skills directory at
   `skills/` (e.g. symlink each into `~/.claude/skills/`, or copy them). Then invoke
   `/deep-research <topic>`.

### Path references — important

The `deep-research/SKILL.md` worker prompts resolve sibling skills by **relative path**
inside the host project, using two historical locations:

- Reddit / Twitter scripts: `"$(git rev-parse --show-toplevel)"/.factory/skills/<skill>/scripts/`
- WeChat CLI: `"$(git rev-parse --show-toplevel)"/.claude/skills/wechat-article/cli/target/release/wxa`
- LinkedIn CLI: `~/.local/bin/linkedin`

When you install into your own project, either (a) place the skills at those paths
(e.g. under `.factory/skills/` and `.claude/skills/`), or (b) edit those path strings
in `skills/deep-research/SKILL.md` to match wherever you put them. The LinkedIn CLI is
expected on PATH at `~/.local/bin/linkedin`.

### WeChat worker (G) — self-hosted

Unlike the others, WeChat has **no public API vendor**. `WECHAT_API_BASE_URL` points at
a backend *you* deploy that proxies the WeChat MP (公众号) endpoints, and `WECHAT_API_KEY`
is tied to a logged-in WeChat MP session — it expires when that session does, and you
refresh it from the browser cookies. See `skills/wechat-article/INSTALL.md` and
`skills/wechat-article/SKILL.md` for the endpoint contract. If you don't research
Chinese-market topics, you can skip this worker entirely.

## How it runs (summary)

`deep-research` works in four phases (full protocol in `skills/deep-research/SKILL.md`):

1. **SCOPE** — define the question; detect named people / companies / Chinese-market relevance.
2. **RETRIEVE** — spawn 3–7 worker subagents *in parallel*, one per data source.
3. **ANALYZE** — cross-reference sources, build a sentiment matrix, flag contradictions.
4. **REPORT** — write an Obsidian-compatible Markdown report to `.archive/reports/YYYY-MM-DD/`.

Workers are added conditionally: persons → Worker D (person-research), company →
Workers E (corporate registry, web-only, no key) + F (LinkedIn), Chinese topic →
Worker G (WeChat).

## Security

`.env` is git-ignored. Never commit real keys. The committed `.env.example` contains
placeholders only.
