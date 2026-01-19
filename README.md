# OSS Funding Dashboard - GitHub Deployment Guide

A static dashboard that displays real-time OSS funding data from Bags.fm, automatically updated every 30 minutes via GitHub Actions.

## Setup Instructions

### 1. Create a New GitHub Repository

1. Go to GitHub and create a new repository
2. Clone it locally or use GitHub's web interface

### 2. Copy These Files

Copy the following files/folders to your repository:
```
.github/
  workflows/
    update-data.yml
scripts/
  fetch_data.py
public/
  index.html
```

### 3. Add Your API Key as a Secret

1. Go to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `BAGS_API_KEY`
5. Value: Your Bags.fm API key
6. Click **Add secret**

### 4. Enable GitHub Pages

1. Go to **Settings** > **Pages**
2. Under "Source", select **Deploy from a branch**
3. Select **main** branch and **/public** folder
4. Click **Save**

### 5. Run the Workflow Manually (First Time)

1. Go to **Actions** tab
2. Click **Update Token Data** workflow
3. Click **Run workflow** > **Run workflow**
4. Wait for it to complete - this creates the initial `data.json`

### 6. Configure Custom Domain (Optional)

If you have a custom domain (e.g., `vibefunded.xyz`):

1. The `public/CNAME` file is already configured with your domain
2. In GitHub, go to **Settings** > **Pages**
3. Under "Custom domain", enter your domain: `vibefunded.xyz`
4. Check "Enforce HTTPS" (after DNS propagates)

**DNS Configuration on Porkbun:**
- Go to your Porkbun domain management
- Add DNS records:
  - **Type:** `CNAME` or `ALIAS`
  - **Name:** `@` (or leave blank for root domain)
  - **Value:** `vishalsachdev.github.io`
  - **TTL:** 600 (or default)

**Note:** DNS propagation can take 5 minutes to 48 hours. Once propagated, GitHub will automatically enable HTTPS.

### 7. Access Your Dashboard

Your dashboard will be available at:
- Custom domain: `https://vibefunded.xyz`
- GitHub Pages: `https://vishalsachdev.github.io/oss-memecoin-ftw/`

## How It Works

1. **GitHub Actions** runs `scripts/fetch_data.py` every 30 minutes
2. The script fetches data from DexScreener and Bags.fm APIs
3. Data is saved to `public/data.json` and committed automatically
4. **GitHub Pages** serves the static `public/index.html` which loads the JSON

## File Structure

```
├── .github/
│   └── workflows/
│       └── update-data.yml    # Automation workflow
├── public/
│   ├── index.html             # Static dashboard
│   ├── CNAME                  # Custom domain configuration
│   └── data.json              # Auto-generated data (created by workflow)
├── scripts/
│   └── fetch_data.py          # Data fetching script
└── README.md
```

## Customization

### Adding New Tokens

Edit the `TOKENS` dictionary in `scripts/fetch_data.py`:

```python
TOKENS = {
    "YOUR_TOKEN": {
        "name": "Token Name",
        "creator": "Creator Name",
        "social": "https://x.com/handle",
        "social_handle": "@handle",
        "project_url": "https://github.com/...",
        "bags_url": "https://bags.fm/...",
        "token_mint": "...",
        "description": "...",
        "pair_address": "..."  # Optional: specific DEX pair
    }
}
```

### Changing Update Frequency

Edit `.github/workflows/update-data.yml` and change the cron schedule:
- `*/30 * * * *` = every 30 minutes
- `0 * * * *` = every hour
- `0 */6 * * *` = every 6 hours

## Troubleshooting

### Data not updating?
- Check the **Actions** tab for failed workflow runs
- Verify your `BAGS_API_KEY` secret is set correctly

### Page not loading?
- Ensure GitHub Pages is enabled and pointing to `/public`
- Wait a few minutes for deployment to propagate

### Missing earnings data?
- The `BAGS_API_KEY` secret might not be set
- Check the workflow logs for API errors
