# Netlify & Web Deployment Guide

The GeoCore project contains both a marketing landing website and a static documentation portal built with Material for MkDocs. This guide explains how to deploy the entire portal to **Netlify** with zero configuration.

---

## 🚀 Quick Deploy to Netlify

### Option 1: Git-Based Automated Deployment (Recommended)
1. Push your changes to GitHub / GitLab / Bitbucket.
2. Log in to [Netlify Dashboard](https://app.netlify.com/).
3. Click **Add new site &rarr; Import an existing project**.
4. Select the `geocore` repository.
5. Netlify will automatically detect `netlify.toml` with the following build settings:
   - **Base directory**: `/` (repository root)
   - **Build command**: `pip install mkdocs mkdocs-material && mkdocs build -d website/docs`
   - **Publish directory**: `website`
6. Click **Deploy Site**. Every subsequent `git push` to `main` will trigger an automated build and deployment.

---

## 🛠️ Option 2: Deploying via Netlify CLI

You can deploy directly from your local terminal using the Netlify CLI:

```bash
# 1. Install Netlify CLI globally
npm install -g netlify-cli

# 2. Build the documentation into website/docs
python -m mkdocs build -d website/docs

# 3. Preview deployment in a draft sandbox
netlify deploy --dir=website

# 4. Deploy to live production URL
netlify deploy --dir=website --prod
```

---

## ⚙️ Configuration Files Included in GeoCore

| File | Purpose |
| :--- | :--- |
| **`netlify.toml`** | Main Netlify deployment manifest specifying build commands, environment variables, headers, and redirects. |
| **`website/_redirects`** | Netlify clean URL rules ensuring `/docs` and `/docs/*` route smoothly to the documentation portal. |
| **`website/_headers`** | High-performance cache policies and strict HTTP security headers (HSTS, CSP, X-Frame-Options). |
