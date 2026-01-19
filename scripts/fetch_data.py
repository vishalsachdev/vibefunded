#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

BAGS_API_KEY = os.environ.get("BAGS_API_KEY", "")

TOKENS = {
    "GAS": {
        "name": "Gastown",
        "creator": "Steve Yegge",
        "social": "https://x.com/Steve_Yegge",
        "social_handle": "@Steve_Yegge",
        "project_url": "https://github.com/steveyegge/gastown",
        "bags_url": "https://bags.fm/7pskt3A1Zsjhngazam7vHWjWHnfgiRump916Xj7ABAGS",
        "token_mint": "7pskt3A1Zsjhngazam7vHWjWHnfgiRump916Xj7ABAGS",
        "description": "Multi-agent AI orchestrator; royalties fund ongoing development of complex agent systems.",
        "pair_address": "finu5nsfwvjqbafdesxdxvlhqja3h7qybrluqfrb27v9"
    },
    "RALPH": {
        "name": "Ralph Wiggum Technique",
        "creator": "Geoffrey Huntley",
        "social": "https://x.com/geoffreyhuntley",
        "social_handle": "@geoffreyhuntley",
        "project_url": "https://ralphcoin.org/",
        "bags_url": "https://bags.fm/CxWPdDBqxVo3fnTMRTvNuSrd4gkp78udSrFvkVDBAGS",
        "token_mint": "CxWPdDBqxVo3fnTMRTvNuSrd4gkp78udSrFvkVDBAGS",
        "description": "Autonomous AI coding loops; royalties support open AI research and esoteric experiments.",
        "pair_address": "DbyK8gEiXwNeh2zFW2Lo1svUQ1WkHAeQyNDsRaKQ6BHf"
    },
    "GSD": {
        "name": "Get Shit Done",
        "creator": "Lex Christopherson",
        "social": "https://x.com/official_taches",
        "social_handle": "@official_taches",
        "project_url": "https://github.com/glittercowboy/get-shit-done",
        "bags_url": "https://bags.fm/8116V1BW9zaXUM6pVhWVaAduKrLcEBi3RGXedKTrBAGS",
        "token_mint": "8116V1BW9zaXUM6pVhWVaAduKrLcEBi3RGXedKTrBAGS",
        "description": "Vibe-coding automation tool; royalties provide risk-free OSS maintenance funding.",
        "pair_address": "dwudwjvan7bzkw9zwlbyv6kspdlvhwzrqy6ebk8xzxkv"
    },
    "LEON": {
        "name": "LEON AI",
        "creator": "Gren Louis",
        "social": "https://x.com/grenlouis",
        "social_handle": "@grenlouis",
        "project_url": "https://github.com/leon-ai",
        "bags_url": "https://bags.fm/Fnmq5udTPPkxGjw8nDtnRsjJWfHfdNmsfKGLhUerBAGS",
        "token_mint": "Fnmq5udTPPkxGjw8nDtnRsjJWfHfdNmsfKGLhUerBAGS",
        "description": "Open-source personal assistant; royalties support ongoing AI development.",
        "pair_address": "GZUPT46aogt2j3HFZiBa4bikNx1K4f525B9hAsTBGLA7"
    }
}

def fetch_sol_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("solana", {}).get("usd", 0)
    except Exception:
        return 0

def fetch_bags_earnings(token_mint):
    if not BAGS_API_KEY or not token_mint:
        return None
    try:
        url = f"https://public-api-v2.bags.fm/api/v1/token-launch/lifetime-fees?tokenMint={token_mint}"
        headers = {"x-api-key": BAGS_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            raw_value = data.get("response", 0)
            if raw_value:
                lamports = float(raw_value)
                sol_value = lamports / 1_000_000_000
                return sol_value
        return None
    except Exception:
        return None

def fetch_dexscreener_data(ticker, pair_address=None):
    try:
        if pair_address:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("pair"):
                return data["pair"]
            return None
        
        url = f"https://api.dexscreener.com/latest/dex/search?q={ticker}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("pairs"):
            return None
        
        solana_pairs = [p for p in data["pairs"] if p.get("chainId") == "solana"]
        
        if not solana_pairs:
            return None
        
        raydium_pairs = [p for p in solana_pairs if p.get("dexId") == "raydium"]
        pairs_to_check = raydium_pairs if raydium_pairs else solana_pairs
        
        best_pair = max(pairs_to_check, key=lambda x: float(x.get("volume", {}).get("h24", 0) or 0))
        
        return best_pair
    except Exception:
        return None

def fetch_github_stats(project_url):
    """Fetch GitHub repository statistics"""
    if not project_url or "github.com" not in project_url:
        return None
    
    try:
        # Extract owner/repo from URL
        # e.g., https://github.com/steveyegge/gastown -> steveyegge/gastown
        parts = project_url.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
        if not parts:
            return None
        
        # GitHub API for public repos (no auth needed, but rate limited to 60/hour)
        url = f"https://api.github.com/repos/{parts}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "VibeFunded-Dashboard"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("watchers_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "language": data.get("language", "N/A"),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "description": data.get("description", "")
            }
        return None
    except Exception as e:
        print(f"  Error fetching GitHub stats: {e}")
        return None

def calculate_pair_age(pair_created_at):
    if not pair_created_at:
        return "N/A"
    try:
        created_time = datetime.fromtimestamp(pair_created_at / 1000)
        now = datetime.now()
        delta = now - created_time
        
        if delta.days > 365:
            return f"{delta.days // 365}y {(delta.days % 365) // 30}m"
        elif delta.days > 30:
            return f"{delta.days // 30}m {delta.days % 30}d"
        elif delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h"
        else:
            return f"{delta.seconds // 60}min"
    except:
        return "N/A"

def main():
    print("Fetching SOL price...")
    sol_price = fetch_sol_price()
    print(f"SOL price: ${sol_price}")
    
    token_data = []
    
    for ticker, info in TOKENS.items():
        print(f"Fetching data for {ticker}...")
        pair_address = info.get("pair_address")
        pair = fetch_dexscreener_data(ticker, pair_address)
        
        token_mint = info.get("token_mint", "")
        earnings = fetch_bags_earnings(token_mint) if token_mint else None
        earnings_usd = earnings * sol_price if earnings and sol_price else 0
        
        # Fetch GitHub stats
        github_stats = fetch_github_stats(info.get("project_url", ""))
        
        if pair:
            price_changes = pair.get("priceChange", {})
            token_data.append({
                "ticker": f"${ticker}",
                "name": info["name"],
                "creator": info["creator"],
                "social": info.get("social", ""),
                "social_handle": info.get("social_handle", ""),
                "project_url": info.get("project_url", ""),
                "bags_url": info.get("bags_url", ""),
                "earnings": earnings if earnings else 0,
                "earnings_usd": earnings_usd,
                "description": info["description"],
                "price": float(pair.get("priceUsd", 0) or 0),
                "fdv": float(pair.get("fdv", 0) or 0),
                "volume_24h": float(pair.get("volume", {}).get("h24", 0) or 0),
                "liquidity": float(pair.get("liquidity", {}).get("usd", 0) or 0),
                "change_5m": float(price_changes.get("m5", 0) or 0),
                "change_1h": float(price_changes.get("h1", 0) or 0),
                "change_6h": float(price_changes.get("h6", 0) or 0),
                "change_24h": float(price_changes.get("h24", 0) or 0),
                "pair_age": calculate_pair_age(pair.get("pairCreatedAt")),
                "url": pair.get("url", f"https://dexscreener.com/solana/{pair.get('pairAddress', '')}"),
                "pair_address": pair.get("pairAddress", ""),
                "active": True,
                "github_stars": github_stats.get("stars", 0) if github_stats else 0,
                "github_forks": github_stats.get("forks", 0) if github_stats else 0,
                "github_watchers": github_stats.get("watchers", 0) if github_stats else 0,
                "github_language": github_stats.get("language", "N/A") if github_stats else "N/A"
            })
        else:
            token_data.append({
                "ticker": f"${ticker}",
                "name": info["name"],
                "creator": info["creator"],
                "social": info.get("social", ""),
                "social_handle": info.get("social_handle", ""),
                "project_url": info.get("project_url", ""),
                "bags_url": info.get("bags_url", ""),
                "earnings": earnings if earnings else 0,
                "earnings_usd": earnings_usd,
                "description": info["description"],
                "price": 0,
                "fdv": 0,
                "volume_24h": 0,
                "liquidity": 0,
                "change_5m": 0,
                "change_1h": 0,
                "change_6h": 0,
                "change_24h": 0,
                "pair_age": "N/A",
                "url": "",
                "pair_address": "",
                "active": False,
                "github_stars": github_stats.get("stars", 0) if github_stats else 0,
                "github_forks": github_stats.get("forks", 0) if github_stats else 0,
                "github_watchers": github_stats.get("watchers", 0) if github_stats else 0,
                "github_language": github_stats.get("language", "N/A") if github_stats else "N/A"
            })
    
    active_tokens = [t for t in token_data if t["active"]]
    total_mcap = sum(t["fdv"] for t in active_tokens)
    total_volume = sum(t["volume_24h"] for t in active_tokens)
    total_earnings = sum(t["earnings_usd"] for t in token_data)
    avg_change = sum(t["change_24h"] for t in active_tokens) / len(active_tokens) if active_tokens else 0
    
    output = {
        "updated_at": datetime.now().isoformat(),
        "sol_price": sol_price,
        "summary": {
            "total_mcap": total_mcap,
            "total_volume": total_volume,
            "total_earnings": total_earnings,
            "avg_change_24h": avg_change,
            "active_tokens": len([t for t in active_tokens if t["volume_24h"] > 1000])
        },
        "tokens": token_data
    }
    
    os.makedirs("public", exist_ok=True)
    
    with open("public/data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nData saved to public/data.json")
    print(f"Total tokens: {len(token_data)}")
    print(f"Active tokens: {len(active_tokens)}")
    print(f"Total earnings: ${total_earnings:,.0f}")

if __name__ == "__main__":
    main()
