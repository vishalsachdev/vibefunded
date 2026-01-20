# VibeFunded Dashboard

Dashboard tracking OSS-funded tokens on Solana via Bags.fm royalties.

## Quick Start

```bash
# Fetch latest token data (prices, earnings, GitHub stats)
python scripts/fetch_data.py

# Data is saved to:
# - data.json (root)
# - public/data.json (for frontend)
# - data/history/{timestamp}.json (historical snapshots)
```

## Data That Needs Manual/Agent Updates

The script auto-fetches most data, but these fields require manual updates:

### 1. Twitter Followers (via browser)
**Why:** Twitter API requires $100/month Basic plan for user lookups.

**How to update:**
1. Visit each creator's X/Twitter profile
2. Note the follower count
3. Update `twitter_followers` field in `data.json` for each token

**Profiles to check:**
| Token | Handle | Profile URL |
|-------|--------|-------------|
| $GAS | @Steve_Yegge | https://x.com/Steve_Yegge |
| $RALPH | @GeoffreyHuntley | https://x.com/geoffreyhuntley |
| $GSD | @official_taches | https://x.com/official_taches |
| $LEON | @grenlouis | https://x.com/grenlouis |

### 2. New Token Additions

New tokens are submitted via GitHub Issues using the template at `.github/ISSUE_TEMPLATE/submit-project.yml`.

**Required fields from submission:**
| Issue Field | Maps To |
|-------------|---------|
| Token Symbol | `TICKER` key |
| Project Name | `name` |
| Creator Name | `creator` |
| Creator Social Handle | `social_handle` and `social` URL |
| Project Description | `description` |
| GitHub/Code Repository | `project_url` |
| Token Mint Address | `token_mint` |
| Bags.fm URL | `bags_url` |
| DexScreener Pair Address | `pair_address` |

To add, update `TOKENS` dict in `scripts/fetch_data.py`:

```python
"TICKER": {
    "name": "Project Name",
    "creator": "Creator Name",
    "social": "https://x.com/handle",
    "social_handle": "@handle",
    "project_url": "https://github.com/owner/repo",
    "bags_url": "https://bags.fm/...",
    "token_mint": "...",  # Solana token mint address
    "description": "Brief description",
    "pair_address": "..."  # DexScreener pair address
}
```

### 3. Creator Info Corrections
If creator name or social links are wrong, update in `scripts/fetch_data.py` TOKENS dict.

## Data Sources

| Data | Source | Auto-fetched? |
|------|--------|---------------|
| Token price, FDV, volume | DexScreener API | Yes |
| Earnings (SOL) | Bags.fm API | Yes |
| SOL price | CoinGecko API | Yes |
| GitHub stars, forks, issues | GitHub API | Yes |
| GitHub contributors, PRs | GitHub API | Yes |
| Reddit mentions | Reddit API | Yes |
| HN mentions | Algolia HN API | Yes |
| Twitter followers | Manual/Browser | **No** |

## File Structure

```
vibefunded/
├── data.json                 # Current token data (single source of truth)
├── public/data.json          # Copy for frontend
├── data/
│   └── history/              # Historical snapshots
│       ├── {timestamp}.json  # Per-run snapshots
│       └── {date}.jsonl      # Daily aggregated (one JSON per line)
├── scripts/
│   └── fetch_data.py         # Data fetching script
└── article/                  # Case study content
```

## Current Tokens

| Ticker | Project | Creator | GitHub |
|--------|---------|---------|--------|
| $GAS | Gastown | Steve Yegge | github.com/steveyegge/gastown |
| $RALPH | Ralph Wiggum Technique | Geoffrey Huntley | github.com/ghuntley/how-to-ralph-wiggum |
| $GSD | Get Shit Done | Lex Christopherson | github.com/glittercowboy/get-shit-done |
| $LEON | LEON AI | Louis Grenard | github.com/leon-ai/leon |

## Environment Variables

```bash
BAGS_API_KEY=xxx  # Required for earnings data from Bags.fm
```

## Scheduled Updates

The script runs via GitHub Actions on a schedule. Twitter followers should be updated periodically by an agent using Claude in Chrome.

## Roadmap

- [ ] Add more tokens as they launch on Bags.fm
- [ ] Build frontend dashboard
- [ ] Add historical charts
- [ ] Consider Twitter API integration if budget allows

## Session Log

| Date | Changes |
|------|---------|
| 2026-01-19 | Added $RALPH and $LEON GitHub stats, Twitter followers for all tokens, historical data tracking |
