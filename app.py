import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Realtime OSS Funding via Royalties",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import os

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
        "description": "Autonomous AI coding loops; royalties support open AI research and esoteric experiments."
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
    "CLAUDEFLOW": {
        "name": "ClaudeFlow",
        "creator": "Reuven Cohen",
        "social": "https://github.com/ruvnet",
        "social_handle": "@ruvnet",
        "project_url": "https://github.com/ruvnet",
        "bags_url": "https://bags.fm/AZnYQZUV7UfyxvkhTTgakUtd8J5nvGYtTzmKpkFcBAGS",
        "token_mint": "AZnYQZUV7UfyxvkhTTgakUtd8J5nvGYtTzmKpkFcBAGS",
        "description": "Agent orchestration platform for Claude; multi-agent swarms and autonomous workflows."
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

@st.cache_data(ttl=60)
def fetch_sol_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("solana", {}).get("usd", 0)
    except Exception:
        return 0

@st.cache_data(ttl=60)
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
    except Exception as e:
        return None

@st.cache_data(ttl=60)
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
    except Exception as e:
        return None

def format_number(value, prefix="$", decimals=2):
    if value is None or value == 0:
        return f"{prefix}0"
    if value >= 1_000_000_000:
        return f"{prefix}{value/1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"{prefix}{value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{prefix}{value/1_000:.{decimals}f}K"
    else:
        return f"{prefix}{value:.{decimals}f}"

def format_price(value):
    if value is None:
        return "$0"
    if value < 0.0001:
        return f"${value:.8f}"
    elif value < 0.01:
        return f"${value:.6f}"
    elif value < 1:
        return f"${value:.4f}"
    else:
        return f"${value:.2f}"

def get_change_color(change):
    if change is None:
        return "gray"
    return "green" if change >= 0 else "red"

def format_change(change):
    if change is None:
        return "N/A"
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}%"

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

with st.sidebar:
    st.header("Dashboard Controls")
    
    refresh_options = {"30 seconds": 30000, "60 seconds": 60000, "Manual only": None}
    refresh_choice = st.selectbox("Auto-refresh interval", list(refresh_options.keys()), index=1)
    refresh_interval = refresh_options[refresh_choice]
    
    volume_filter = st.number_input(
        "Minimum 24h Volume ($)", 
        min_value=0, 
        max_value=1000000, 
        value=0, 
        step=1000,
        help="Filter tokens with 24h volume greater than this amount"
    )

if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = {}

if refresh_interval:
    count = st_autorefresh(interval=refresh_interval, limit=None, key="data_refresh")

st.title("Realtime OSS Funding via Royalties")
st.markdown("### Bags.fm Creator Memecoin Dashboard")
st.markdown("""
Visualizing how Bags.fm's royalty model turns speculative trading into sustainable funding 
for vibe-coded open source and AI projects (as of Jan 2026).
""")

with st.expander("Notes", expanded=False):
    st.markdown("""
**Key Insights:**

- **Bags.fm enables OSS creators or any community member to launch memecoins** with built-in royalty mechanisms
- **Trading volume directly translates to creator funding** via royalties
- **This model disrupts traditional grant/VC funding** for open source
- **Network effects drive sustainable, perpetual revenue** for maintainers
- **"Vibe-coded" projects** combine AI tools with community-driven funding
""")

header_cols = st.columns([3, 1])
with header_cols[1]:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

if refresh_interval:
    st.caption(f"Data refreshes every {refresh_interval // 1000} seconds")
else:
    st.caption("Auto-refresh disabled - use the Refresh button above")

all_tokens = {**TOKENS, **st.session_state.get("custom_tickers", {})}

with st.spinner("Fetching live data from DexScreener..."):
    token_data = []
    sol_price = fetch_sol_price()
    
    for ticker, info in all_tokens.items():
        pair_address = info.get("pair_address")
        pair = fetch_dexscreener_data(ticker, pair_address)
        
        bags_url = info.get("bags_url", "")
        token_mint = info.get("token_mint", "")
        earnings = fetch_bags_earnings(token_mint) if token_mint else None
        earnings_usd = earnings * sol_price if earnings and sol_price else 0
        
        if pair:
            price_changes = pair.get("priceChange", {})
            token_data.append({
                "ticker": f"${ticker}",
                "name": info["name"],
                "creator": info["creator"],
                "social": info.get("social", ""),
                "social_handle": info.get("social_handle", ""),
                "project_url": info.get("project_url", ""),
                "bags_url": bags_url,
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
                "active": True
            })
        else:
            token_data.append({
                "ticker": f"${ticker}",
                "name": info["name"],
                "creator": info["creator"],
                "social": info.get("social", ""),
                "social_handle": info.get("social_handle", ""),
                "project_url": info.get("project_url", ""),
                "bags_url": bags_url,
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
                "active": False
            })

df = pd.DataFrame(token_data)

if volume_filter > 0:
    df_filtered = df[df["volume_24h"] >= volume_filter]
else:
    df_filtered = df

active_df = df_filtered[df_filtered["active"]]

st.markdown("---")
st.subheader("Summary Metrics")

kpi_cols = st.columns(5)

total_mcap = active_df["fdv"].sum()
with kpi_cols[0]:
    st.metric("Total Market Cap", format_number(total_mcap))

total_volume = active_df["volume_24h"].sum()
with kpi_cols[1]:
    st.metric("Total 24h Volume", format_number(total_volume))

active_tokens = len(active_df[active_df["volume_24h"] > 1000])
with kpi_cols[2]:
    st.metric("Active Tokens (Vol > $1K)", str(active_tokens))

avg_change = active_df["change_24h"].mean() if len(active_df) > 0 else 0
with kpi_cols[3]:
    st.metric("Avg 24h Change", format_change(avg_change))

if len(active_df) > 0:
    highest_vol_token = active_df.loc[active_df["volume_24h"].idxmax()]
    highest_vol_name = highest_vol_token["ticker"]
else:
    highest_vol_name = "N/A"
with kpi_cols[4]:
    st.metric("Highest Volume", highest_vol_name)

st.markdown("---")
st.subheader("Token Overview")

if "selected_tokens" not in st.session_state:
    st.session_state.selected_tokens = []

if len(df_filtered) > 0:
    display_df = df_filtered.copy()
    
    display_df["Price"] = display_df["price"].apply(format_price)
    display_df["FDV/MC"] = display_df["fdv"].apply(lambda x: format_number(x))
    display_df["24h Volume"] = display_df["volume_24h"].apply(lambda x: format_number(x))
    display_df["Liquidity"] = display_df["liquidity"].apply(lambda x: format_number(x))
    display_df["Status"] = display_df["active"].apply(lambda x: "Active" if x else "Inactive/No Data")
    display_df["Earnings (USD)"] = display_df["earnings_usd"].apply(lambda x: f"${x:,.0f}" if x and x > 0 else "N/A")
    display_df["Earnings (SOL)"] = display_df["earnings"].apply(lambda x: f"{x:,.2f} SOL" if x and x > 0 else "N/A")
    
    def format_change_colored(change):
        if change is None or change == 0:
            return "0.00%"
        sign = "+" if change >= 0 else ""
        return f"{sign}{change:.2f}%"
    
    display_df["5m"] = display_df["change_5m"].apply(format_change_colored)
    display_df["1h"] = display_df["change_1h"].apply(format_change_colored)
    display_df["6h"] = display_df["change_6h"].apply(format_change_colored)
    display_df["24h"] = display_df["change_24h"].apply(format_change_colored)
    
    table_df = display_df[["ticker", "name", "project_url", "creator", "social", "bags_url", "Earnings (USD)", "Earnings (SOL)", "pair_age", "Price", "FDV/MC", "24h Volume", 
                            "Liquidity", "url", "5m", "1h", "6h", "24h", "Status"]].copy()
    table_df.columns = ["Ticker", "Project Name", "Project", "Creator", "Social", "Bags.fm", "Earnings (USD)", "Earnings (SOL)", "Days from Launch", "Price", "FDV/MC", "24h Volume", 
                        "Liquidity", "DexScreener", "5m", "1h", "6h", "24h", "Status"]
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Project Name": st.column_config.TextColumn("Project Name", width="medium"),
            "Project": st.column_config.LinkColumn("Project", display_text="View", width="small"),
            "Creator": st.column_config.TextColumn("Creator", width="small"),
            "Social": st.column_config.LinkColumn("Social", display_text="View", width="small"),
            "Bags.fm": st.column_config.LinkColumn("Bags.fm", display_text="View", width="small"),
            "Earnings (USD)": st.column_config.TextColumn("Earnings (USD)", width="small"),
            "Earnings (SOL)": st.column_config.TextColumn("Earnings (SOL)", width="small"),
            "Days from Launch": st.column_config.TextColumn("Days from Launch", width="small"),
            "Price": st.column_config.TextColumn("Price", width="small"),
            "FDV/MC": st.column_config.TextColumn("FDV/MC", width="small"),
            "24h Volume": st.column_config.TextColumn("24h Volume", width="small"),
            "Liquidity": st.column_config.TextColumn("Liquidity", width="small"),
            "DexScreener": st.column_config.LinkColumn("DexScreener", display_text="View", width="small"),
            "5m": st.column_config.TextColumn("5m", width="small"),
            "1h": st.column_config.TextColumn("1h", width="small"),
            "6h": st.column_config.TextColumn("6h", width="small"),
            "24h": st.column_config.TextColumn("24h", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        }
    )
    
    total_earnings_usd = display_df["earnings_usd"].sum()
    st.markdown(f"**Total Earnings: ${total_earnings_usd:,.0f}**")
    
    st.markdown("**Price Change Legend:** Green = positive, Red = negative")
    change_cols = st.columns(8)
    for i, (_, row) in enumerate(display_df.iterrows()):
        if i >= 8:
            break
        with change_cols[i % 8]:
            color_5m = "#22c55e" if row["change_5m"] >= 0 else "#ef4444"
            color_1h = "#22c55e" if row["change_1h"] >= 0 else "#ef4444"
            color_6h = "#22c55e" if row["change_6h"] >= 0 else "#ef4444"
            color_24h = "#22c55e" if row["change_24h"] >= 0 else "#ef4444"
            st.markdown(f"""
            **{row['ticker']}**  
            <span style="color:{color_5m}">5m: {row['5m']}</span>  
            <span style="color:{color_1h}">1h: {row['1h']}</span>  
            <span style="color:{color_6h}">6h: {row['6h']}</span>  
            <span style="color:{color_24h}">24h: {row['24h']}</span>
            """, unsafe_allow_html=True)
else:
    st.warning("No tokens match the current filter criteria.")


st.markdown("---")
st.caption("""
Data from DexScreener API & Bags.fm API • Built for Bags.fm OSS Funding Case Study • Jan 2026 • DYOR – crypto is volatile
""")
