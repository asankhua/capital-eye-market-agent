# Render.com Deployment Guide

## Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/asankhua/capital-eye-market-agent)

## Manual Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Create Web Service on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo: `asankhua/capital-eye-market-agent`
4. Configure:
   - **Name**: `capital-eye-market-agent`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt && cd frontend/react-directory && npm ci && npm run build`
   - **Start Command**: `python3 -m uvicorn backend.api.fastapi_server:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables

In Render Dashboard → Your Service → Environment:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | *Your Groq API Key* |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `LLM_PROVIDER` | `groq` |
| `API_BASE_URL` | `https://your-service-name.onrender.com` |
| `REACT_APP_API_URL` | `https://your-service-name.onrender.com` |
| `LOG_LEVEL` | `INFO` |

### 4. Deploy

Click **"Deploy"** and wait for build to complete.

## Using render.yaml (Blueprints)

If you have the `render.yaml` in your repo:

1. Go to Render Dashboard
2. Click **"Blueprints"** → **"New Blueprint Instance"**
3. Connect your repo
4. Render will auto-configure the service

## Troubleshooting

### Build Failures
- Check that `package.json` exists in `frontend/react-directory/`
- Ensure Node.js 18+ is used

### Frontend Not Loading
- Check that `npm run build` creates `frontend/react-directory/dist/`
- Verify `FRONTEND_DIST` path in logs

### API Errors
- Verify `GROQ_API_KEY` is set correctly
- Check logs in Render Dashboard

## URLs

- **Live App**: `https://capital-eye-market-agent.onrender.com`
- **API Docs**: `https://capital-eye-market-agent.onrender.com/docs`
- **Health Check**: `https://capital-eye-market-agent.onrender.com/health`
