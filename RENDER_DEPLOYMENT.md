# Deploying to Render

This guide will help you deploy the Lead Generation API to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Prepare Your Repository

Make sure your repository includes:
- `server.py` - Flask server
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration (optional but recommended)
- All your project files (toolkit/, functions/, pipeline/, etc.)

## Step 2: Create a New Web Service on Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository
4. Render will auto-detect it's a Python service

## Step 3: Configure the Service

### Basic Settings:
- **Name**: `lead-generation-api` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn server:app`

### Advanced Settings:
- **Auto-Deploy**: `Yes` (deploys on every push to main branch)
- **Health Check Path**: `/` (optional)

## Step 4: Add Environment Variables

Go to **Environment** tab and add all required API keys:

### Required Environment Variables:
```
APIFY_API_TOKEN=your_apify_token
NEVERBOUNCE_API_KEY=your_neverbounce_key
PERPLEXITY_API_KEY=your_perplexity_key
OPENAI_API_KEY=your_openai_key
INSTANTLY_API_KEY=your_instantly_key
BRIGHTDATA_BEARER_TOKEN=your_brightdata_token
WEBHOOK_URL=your_webhook_url
```

### Optional Environment Variables:
```
HUBSPOT_API_KEY=your_hubspot_key (if using HubSpot pipeline)
FLASK_ENV=production
```

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start the server with gunicorn
   - Provide you with a URL (e.g., `https://lead-generation-api.onrender.com`)

## Step 6: Test Your Deployment

Once deployed, test the endpoints:

```bash
# Health check
curl https://your-app.onrender.com/

# Start Apollo pipeline
curl -X POST https://your-app.onrender.com/apollo

# Check status
curl https://your-app.onrender.com/status/apollo
```

## Important Notes

### File Storage:
- Render provides **ephemeral disk storage** - files are deleted when the service restarts
- Your pipelines upload files to Google Drive and delete local copies
- This is perfect for your use case!

### Resource Limits (Free Tier):
- **512 MB RAM**
- **0.1 CPU**
- **100 GB bandwidth/month**
- Services **spin down after 15 minutes of inactivity** (takes ~30 seconds to wake up)

### Upgrading (Paid Plans):
- More RAM and CPU
- No spin-down (always on)
- Better performance for long-running pipelines

### Monitoring:
- Check logs in Render dashboard
- Monitor resource usage
- Set up alerts for errors

## Troubleshooting

### Service won't start:
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `gunicorn` is in requirements.txt

### Pipelines timing out:
- Free tier has request timeout limits
- Consider upgrading or optimizing pipeline steps
- Use background jobs for long-running tasks

### Files not found:
- Remember: Render's disk is ephemeral
- Files are deleted on restart
- Make sure uploads to Google Drive work correctly

## Alternative: Using render.yaml

If you included `render.yaml` in your repo, you can use Render's Blueprint feature:

1. Go to **Dashboard** → **New +** → **Blueprint**
2. Connect your repository
3. Render will read `render.yaml` and create the service automatically
4. You'll still need to add environment variables manually

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

