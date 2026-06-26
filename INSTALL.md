# INSTALL — agent-followable setup guide

This is a deterministic, step-by-step install for an autonomous agent (or a human).
Run the steps in order. Each step has a **verify** command — if it fails, fix that step
before moving on. Commands assume macOS/Linux + `zsh`/`bash`.

> Goal: make `/deep-research` runnable, with whichever workers the user needs active.
> You do **not** need every API key — see [Step 5](#step-5--api-keys-fill-only-what-you-need).

---

## Step 0 — Prerequisites

Install these if missing:

| Tool | Check | Install |
|------|-------|---------|
| git | `git --version` | preinstalled / `brew install git` |
| Python ≥ 3.12 | `python3 --version` | `brew install python@3.12` |
| uv | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Rust + cargo | `cargo --version` | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |

Rust/cargo is only needed if you want the **LinkedIn** (Worker F) or **WeChat** (Worker G)
CLIs. Skip it otherwise.

**Verify:** `python3 --version && uv --version` print versions.

---

## Step 1 — Clone

```bash
git clone https://github.com/Jing-yilin/deep-research-skill.git
cd deep-research-skill
```

**Verify:** `ls skills` lists `deep-research reddit twitter linkedin wechat-article person-research youtube scrapecreators-api`.

---

## Step 2 — Shared Python environment (all Python skills)

All Python skills share **one** uv env defined by the root `pyproject.toml`.

```bash
uv sync
source .venv/bin/activate
```

**Verify:**
```bash
python3 -c "import composio, requests, toon_format; print('deps OK')"
```
Expect: `deps OK`.

> Scripts add their own `scripts/` dir to `sys.path`, so local sibling imports
> (`from credential import ...`) work no matter where you launch them — as long as
> this venv is active.

---

## Step 3 — Build the LinkedIn CLI (Worker F) — optional

Skip if you won't use LinkedIn intel.

```bash
cd skills/linkedin/cli
cargo build --release
mkdir -p ~/.local/bin
cp target/release/linkedin ~/.local/bin/linkedin
cd ../../..
```

**Verify:** `~/.local/bin/linkedin --help` prints usage. Ensure `~/.local/bin` is on `PATH`
(`echo $PATH | tr ':' '\n' | grep -q "$HOME/.local/bin" && echo "on PATH" || echo 'add: export PATH="$HOME/.local/bin:$PATH"'`).

---

## Step 4 — Build the WeChat CLI (Worker G) — optional

Skip unless you research Chinese-market topics. Requires a self-hosted backend (Step 5).

```bash
cd skills/wechat-article/cli
cargo build --release
cd ../../..
```

**Verify:** `skills/wechat-article/cli/target/release/wxa --help` prints usage.

---

## Step 5 — API keys (fill only what you need)

```bash
cp .env.example .env
# edit .env, then load it into the shell:
set -a; source .env; set +a
```

Workers auto-skip when their key is absent. Pick the minimum for your use case:

| Worker / feature | Env var(s) | Required? | Get key at |
|---|---|---|---|
| Web (Worker A) | — | none (harness `WebSearch`) | — |
| Reddit basic (Worker B) | — | none (public JSON API) | — |
| Reddit enhanced sorts | `SCRAPECREATORS_API_KEY` | optional | https://scrapecreators.com |
| Twitter/X (Worker C) | `TWITTERAPI_API_KEY` | required for Twitter | https://twitterapi.io |
| LinkedIn (Worker F) | `HARVESTAPI_API_KEY` | required for LinkedIn | https://harvest-api.com |
| WeChat (Worker G) | `WECHAT_API_BASE_URL`, `WECHAT_API_KEY` | required for WeChat | self-hosted — see `skills/wechat-article/INSTALL.md` |
| person-research media | `YOUTUBE_API_KEY`, `TRANSCRIPT_API_KEY` | optional | Google Cloud / https://www.transcriptapi.com |
| person-research enrich | `HUNTER_API_KEY`, `PEOPLEDATALABS_API_KEY` | optional | https://hunter.io / https://peopledatalabs.com |
| write ops (not used by deep-research) | `COMPOSIO_API_KEY` | optional | https://composio.dev |

**Verify (per key you set):**
```bash
# Twitter
python3 skills/twitter/scripts/search_tweets.py "openai" --type Top --limit 2
# LinkedIn
~/.local/bin/linkedin search-companies "OpenAI"
# ScrapeCreators credit balance
curl -s https://api.scrapecreators.com/v1/credit/balance -H "x-api-key: $SCRAPECREATORS_API_KEY"
```
A non-error response (or data) means the key works.

---

## Step 6 — Register the skills with your agent harness

The `/deep-research` orchestrator spawns workers that resolve sibling skills by path.
Make the skills discoverable to your harness. Two options:

**Option A — symlink into the harness skills dir** (e.g. Claude Code):
```bash
mkdir -p ~/.claude/skills
for s in deep-research reddit twitter linkedin wechat-article person-research youtube scrapecreators-api; do
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/"$s"
done
```

**Option B — copy into your project** at the paths the worker prompts expect.

### Path references the orchestrator hardcodes

`skills/deep-research/SKILL.md` worker prompts reference siblings via these paths:

| Worker | Path it expects |
|--------|-----------------|
| Reddit / Twitter scripts | `"$(git rev-parse --show-toplevel)"/.factory/skills/<skill>/scripts/` |
| WeChat CLI | `"$(git rev-parse --show-toplevel)"/.claude/skills/wechat-article/cli/target/release/wxa` |
| LinkedIn CLI | `~/.local/bin/linkedin` |

If your install location differs, either place the skills at those paths
(e.g. under `.factory/skills/` and `.claude/skills/` in your working project),
**or** edit those path strings in `skills/deep-research/SKILL.md` to match.
The LinkedIn CLI must be at `~/.local/bin/linkedin` (Step 3 does this).

**Verify:** your harness lists `deep-research` among available skills.

---

## Step 7 — Run

In your agent, invoke:
```
/deep-research <topic>
```
The skill runs SCOPE → RETRIEVE (parallel workers) → ANALYZE → REPORT, writing a
Markdown report to `.archive/reports/YYYY-MM-DD/<topic-slug>.md`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: toon_format` | venv not active | `source .venv/bin/activate` (Step 2) |
| `error: TWITTERAPI_API_KEY not set` | key not exported | set it in `.env`, `set -a; source .env; set +a` |
| Reddit `HTTP 403` | network/IP blocked by Reddit, or rate-limited | retry later / different network; basic Reddit needs no key |
| `linkedin: command not found` | CLI not built or not on PATH | Step 3, and add `~/.local/bin` to PATH |
| `wxa` auth errors (`密钥已过期`/`invalid session`) | WeChat key tied to expired MP session | refresh `WECHAT_API_KEY` from browser cookies (see wechat-article INSTALL.md) |
| Worker can't find a sibling skill | path mismatch | reconcile install paths with Step 6's table |

## Minimal install recipes

- **Web + Reddit only:** Steps 0–2, 6, 7. No keys.
- **+ Twitter:** also set `TWITTERAPI_API_KEY` (Step 5).
- **+ Company/team due diligence:** also Step 3 + `HARVESTAPI_API_KEY`.
- **+ Chinese-market topics:** also Step 4 + `WECHAT_API_BASE_URL`/`WECHAT_API_KEY`.
