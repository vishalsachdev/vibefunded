# Setup Instructions

## GitHub Pages Configuration

**IMPORTANT:** You need to configure GitHub Pages to serve from the `/public` folder, not the root.

1. Go to: https://github.com/vishalsachdev/oss-memecoin-ftw/settings/pages
2. Under "Source", select **Deploy from a branch**
3. Select **main** branch
4. Select **/public** folder (NOT root)
5. Click **Save**

## Custom Domain Setup

1. In the same Pages settings, under "Custom domain", enter: `vibefunded.xyz`
2. Check "Enforce HTTPS" (after DNS propagates)

## API Key Setup

1. Go to: https://github.com/vishalsachdev/oss-memecoin-ftw/settings/secrets/actions
2. Click **New repository secret**
3. Name: `BAGS_API_KEY`
4. Value: Your Bags.fm API key
5. Click **Add secret**

## First Run

1. Go to: https://github.com/vishalsachdev/oss-memecoin-ftw/actions
2. Click **Update Token Data** workflow
3. Click **Run workflow** > **Run workflow**
4. Wait for it to complete - this creates the initial `data.json`
