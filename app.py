import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Bags.fm Creator Memecoin Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

TOKENS = {
    "GAS": {
        "name": "Gastown",
        "creator": "Steve Yegge (@SteveYegge)",
        "description": "Multi-agent AI orchestrator; royalties fund ongoing development of complex agent systems."
    },
    "RALPH": {
        "name": "Ralph Wiggum Technique",
        "creator": "Geoffrey Huntley (@geoffhuntley)",
        "description": "Autonomous AI coding loops; royalties support open AI research and esoteric experiments."
    },
    "TETSUO": {
        "name": "Tetsuo Corp / solprivacy",
        "creator": "@tetsuoai / @tetsuoarena",
        "description": "Open-source Solana privacy tools and AI agents; funds hardware/robotics experiments."
    },
    "GSD": {
        "name": "Get Shit Done",
        "creator": "Anonymous/Claude Code community",
        "description": "Vibe-coding automation tool; royalties provide risk-free OSS maintenance funding."
    },
    "TEXTUAL": {
        "name": "Textual",
        "creator": "Will McGugan (@willmcgugan)",
        "description": "Python TUI framework; royalties support long-term maintenance of widely used OSS library."
    },
    "SOLPRIV": {
        "name": "solprivacy",
        "creator": "Tetsuo Corp",
        "description": "AI-powered wallet privacy scanner; funds on-chain privacy tooling."
    },
    "FACTORY": {
        "name": "Factory",
        "creator": "Bags ecosystem AI builders",
        "description": "Natural language to app prototyping platform; royalties accelerate full-stack AI builds."
    },
    "OSS": {
        "name": "Meta OSS Funding",
        "creator": "Community",
        "description": "Generic token directing royalties to open-source maintainers; meta-play on sustainable funding."
    }
}

@st.cache_data(ttl=60)
def fetch_dexscreener_data(ticker):
    try:
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
    
    st.divider()
    
    st.subheader("Add Custom Ticker")
    custom_ticker = st.text_input("Ticker symbol (without $)", placeholder="e.g., BONK")
    add_custom = st.button("Add Ticker")
    
    if "custom_tickers" not in st.session_state:
        st.session_state.custom_tickers = {}
    
    if add_custom and custom_ticker:
        custom_ticker = custom_ticker.upper().strip()
        if custom_ticker not in TOKENS and custom_ticker not in st.session_state.custom_tickers:
            st.session_state.custom_tickers[custom_ticker] = {
                "name": custom_ticker,
                "creator": "Custom",
                "description": "User-added token"
            }
            st.success(f"Added ${custom_ticker}")
        elif custom_ticker in TOKENS:
            st.warning(f"${custom_ticker} already exists in the default list")
        else:
            st.warning(f"${custom_ticker} already added")
    
    st.divider()
    
    st.subheader("Case Study Notes")
    st.markdown("""
    **Key Insights:**
    
    - Bags.fm enables OSS creators to launch memecoins with built-in royalty mechanisms
    - Trading volume directly translates to creator funding via royalties
    - This model disrupts traditional grant/VC funding for open source
    - Network effects drive sustainable, perpetual revenue for maintainers
    - "Vibe-coded" projects combine AI tools with community-driven funding
    """)

if refresh_interval:
    count = st_autorefresh(interval=refresh_interval, limit=None, key="data_refresh")

st.title("Bags.fm Creator Memecoin Dashboard")
st.markdown("### Realtime OSS Funding via Royalties")
st.markdown("""
Visualizing how Bags.fm's royalty model turns speculative trading into sustainable funding 
for vibe-coded open source and AI projects (as of Jan 2026).
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
    
    for ticker, info in all_tokens.items():
        pair = fetch_dexscreener_data(ticker)
        
        if pair:
            price_changes = pair.get("priceChange", {})
            token_data.append({
                "ticker": f"${ticker}",
                "name": info["name"],
                "creator": info["creator"],
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

if len(df_filtered) > 0:
    display_df = df_filtered.copy()
    
    display_df["Price"] = display_df["price"].apply(format_price)
    display_df["FDV/MC"] = display_df["fdv"].apply(lambda x: format_number(x))
    display_df["24h Volume"] = display_df["volume_24h"].apply(lambda x: format_number(x))
    display_df["Liquidity"] = display_df["liquidity"].apply(lambda x: format_number(x))
    display_df["5m"] = display_df["change_5m"].apply(format_change)
    display_df["1h"] = display_df["change_1h"].apply(format_change)
    display_df["6h"] = display_df["change_6h"].apply(format_change)
    display_df["24h"] = display_df["change_24h"].apply(format_change)
    display_df["Status"] = display_df["active"].apply(lambda x: "Active" if x else "Inactive/No Data")
    
    table_df = display_df[["ticker", "name", "creator", "Price", "FDV/MC", "24h Volume", 
                            "Liquidity", "5m", "1h", "6h", "24h", "pair_age", "Status"]].copy()
    table_df.columns = ["Ticker", "Project Name", "Creator", "Price", "FDV/MC", "24h Volume", 
                        "Liquidity", "5m", "1h", "6h", "24h", "Pair Age", "Status"]
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Project Name": st.column_config.TextColumn("Project Name", width="medium"),
            "Creator": st.column_config.TextColumn("Creator", width="medium"),
            "Price": st.column_config.TextColumn("Price", width="small"),
            "FDV/MC": st.column_config.TextColumn("FDV/MC", width="small"),
            "24h Volume": st.column_config.TextColumn("24h Volume", width="small"),
            "Liquidity": st.column_config.TextColumn("Liquidity", width="small"),
            "5m": st.column_config.TextColumn("5m", width="small"),
            "1h": st.column_config.TextColumn("1h", width="small"),
            "6h": st.column_config.TextColumn("6h", width="small"),
            "24h": st.column_config.TextColumn("24h", width="small"),
            "Pair Age": st.column_config.TextColumn("Pair Age", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        }
    )
    
    with st.expander("View DexScreener Links"):
        for _, row in df_filtered[df_filtered["active"]].iterrows():
            if row["url"]:
                st.markdown(f"[{row['ticker']} - {row['name']}]({row['url']})")
else:
    st.warning("No tokens match the current filter criteria.")

st.markdown("---")
st.subheader("Volume Analysis")

chart_df = active_df[active_df["volume_24h"] > 0].copy()

if len(chart_df) > 0:
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown("##### 24h Volume Comparison")
        bar_df = chart_df.sort_values("volume_24h", ascending=True)
        fig_bar = px.bar(
            bar_df,
            y="ticker",
            x="volume_24h",
            orientation="h",
            labels={"volume_24h": "24h Volume (USD)", "ticker": "Token"},
            color="volume_24h",
            color_continuous_scale="Viridis"
        )
        fig_bar.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            coloraxis_showscale=False
        )
        fig_bar.update_traces(
            hovertemplate="<b>%{y}</b><br>Volume: $%{x:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with chart_cols[1]:
        st.markdown("##### Volume Distribution")
        fig_pie = px.pie(
            chart_df,
            values="volume_24h",
            names="ticker",
            hole=0.4
        )
        fig_pie.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Volume: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("##### 24h Price Change Overview")
    change_df = chart_df.sort_values("change_24h", ascending=True)
    colors = ["#ef4444" if x < 0 else "#22c55e" for x in change_df["change_24h"]]
    
    fig_change = px.bar(
        change_df,
        y="ticker",
        x="change_24h",
        orientation="h",
        labels={"change_24h": "24h Change (%)", "ticker": "Token"}
    )
    fig_change.update_traces(
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>Change: %{x:.2f}%<extra></extra>"
    )
    fig_change.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="gray")
    )
    st.plotly_chart(fig_change, use_container_width=True)
else:
    st.info("No active tokens with volume data to display charts.")

st.markdown("---")
st.caption("""
Data from DexScreener API • Built for Bags.fm OSS Funding Case Study • Jan 2026 • DYOR – crypto is volatile
""")
