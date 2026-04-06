# Environment Variables for Hugging Face Deployment

## Required Environment Variables (Must Set in Hugging Face Spaces)

| Variable | Description | How to Get | Required |
|----------|-------------|------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM access | https://console.groq.com/keys | **YES** |

## Optional Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_MODEL` | Groq model to use | `llama-3.3-70b-versatile` | No |
| `LLM_PROVIDER` | LLM provider (groq only) | `groq` | No |
| `FINNHUB_API_KEY` | Finnhub API for market data | https://finnhub.io/dashboard | No |
| `TWELVE_DATA_API_KEY` | Twelve Data API alternative | https://twelvedata.com/ | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `LOG_FILE` | Log file path | `dump.log` | No |
| `CACHE_TTL_SECONDS` | Cache time-to-live | `300` | No |

## Hugging Face Deployment Variables

| Variable | Description | Value |
|----------|-------------|-------|
| `PORT` | Server port | `7860` (HF default) |
| `API_BASE_URL` | Backend URL | `http://localhost:7860` |
| `REACT_APP_API_URL` | Frontend API URL | `http://localhost:7860` |

## Setup Instructions for Hugging Face Spaces

1. **Go to your Space Settings:**
   - URL: https://huggingface.co/spaces/ashishsankhua/capital_eye_market_agent/settings

2. **Add Secrets (Environment Variables):**
   - Click "New secret"
   - Add `GROQ_API_KEY` with your actual Groq API key
   - Add any other optional variables as needed

3. **Get Groq API Key:**
   - Visit: https://console.groq.com/keys
   - Create a new API key
   - Copy and paste into HF Spaces secrets

4. **Restart Space:**
   - After adding secrets, restart the Space for changes to take effect

## GitHub Repository Secrets (For Auto-Sync)

| Secret | Description | How to Get |
|--------|-------------|------------|
| `HF_TOKEN` | Hugging Face access token | https://huggingface.co/settings/tokens |

### Setting up HF_TOKEN in GitHub (CRITICAL STEP):

**The sync will FAIL without this step!**

1. **Get HF Token:**
   - Go to: https://huggingface.co/settings/tokens
   - Click "New token"
   - Give it a name (e.g., "GitHub Sync")
   - **Select "Write" role** (required to push code)
   - Click "Generate"
   - **Copy the token immediately** (you won't see it again!)

2. **Add to GitHub:**
   - Go to: https://github.com/asankhua/capital-eye-market-agent/settings/secrets/actions
   - Click "New repository secret"
   - Name: `HF_TOKEN`
   - Value: Paste the token from step 1
   - Click "Add secret"

3. **Verify:**
   - Make any change and push to main branch
   - GitHub Action should successfully sync to HF Spaces

## Files Created/Modified for Deployment

1. `.github/workflows/sync-to-huggingface.yml` - GitHub Action for auto-sync
2. `Dockerfile` - Multi-stage build for HF Spaces
3. `requirements-hf.txt` - HF-specific dependencies
4. Updated `docs/architecture.md` - Added deployment section
5. Updated `docs/case_study.md` - Added deployment guide
6. Updated `README.md` - Added deployment instructions

## Deployment URLs

- **GitHub:** https://github.com/asankhua/capital-eye-market-agent
- **Hugging Face:** https://huggingface.co/spaces/ashishsankhua/capital_eye_market_agent

## Troubleshooting

### Error: "could not read Password for 'https://***@huggingface.co'"
**Cause:** HF_TOKEN secret not set in GitHub
**Fix:** Follow "Setting up HF_TOKEN in GitHub" steps above

### Error: "Repository not found" or "403 Forbidden"
**Cause:** HF_TOKEN doesn't have write access or wrong username/space name
**Fix:** 
1. Regenerate token with "Write" role at https://huggingface.co/settings/tokens
2. Update the secret in GitHub
3. Ensure space name is `capital_eye_market_agent` under user `ashishsankhua`

### Space builds but shows 500 error
**Cause:** Missing GROQ_API_KEY in HF Spaces
**Fix:** Add GROQ_API_KEY secret in https://huggingface.co/spaces/ashishsankhua/capital_eye_market_agent/settings
