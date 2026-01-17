# Bags.fm Creator Memecoin Dashboard

## Overview

This project is an interactive, real-time memecoin dashboard built with Streamlit that tracks creator-focused tokens launched on Bags.fm. The dashboard serves as a supporting artifact for a business school case study examining disruptive funding models in open source software (OSS) and AI development through creator royalty memecoins.

The application fetches live data from the DexScreener public API to display key metrics for predefined Solana-based tokens, including price, market cap, trading volume, and price changes. It targets business school students, researchers, and analysts studying platform strategy, network effects, and innovation in crypto/creator economies.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit (Python-based)
- **Rationale**: Chosen for rapid development of interactive dashboards with minimal code. Streamlit is Replit-friendly, supports caching, auto-refresh capabilities, and integrates well with visualization libraries.
- **Layout**: Wide layout with expandable sidebar for configuration options
- **Visualization**: Plotly Express for interactive charts

### Data Flow Architecture
- **Pattern**: Client-side data fetching with no backend database
- **Rationale**: All data is fetched live from public APIs, eliminating the need for data persistence. This simplifies deployment and ensures real-time accuracy.
- **Caching Strategy**: Results cached for 30-60 seconds to avoid API rate limits
- **Auto-refresh**: Implemented via `streamlit_autorefresh` for real-time updates

### Token Resolution Logic
1. Query DexScreener search endpoint with ticker symbol
2. Filter results to `chainId == "solana"` and preferably `dexId == "raydium"`
3. Select pair with highest 24h volume or liquidity as the "main" pair
4. Fallback: Display "Data unavailable" with manual refresh option if API fails

### Data Model
- **Predefined Token List**: Hardcoded dictionary containing ticker symbols, project names, creators, and descriptions for OSS/AI creator funding tokens
- **Key Metrics Tracked**: Price (USD), FDV/Market Cap, 24h Volume, Liquidity, Price changes (5m, 1h, 6h, 24h), Pair age, DexScreener URLs

## External Dependencies

### APIs
- **DexScreener Public API** (No API key required)
  - Search endpoint: `https://api.dexscreener.com/latest/dex/search?q={query}`
  - Pair details: `https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}`
  - Used for fetching real-time token price data, volume, liquidity, and market metrics

### Python Libraries
- `streamlit` - Web application framework
- `requests` - HTTP client for API calls
- `pandas` - Data manipulation and table display
- `plotly` - Interactive chart visualization
- `streamlit_autorefresh` - Automatic page refresh functionality
- `datetime` and `time` - Timestamp handling and delays

### Deployment
- **Platform**: Replit
- **Type**: Public web application
- **Authentication**: None required (public dashboard)