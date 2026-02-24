# Scout Deployment Guide — Vercel

## Prerequisites
- GitHub repo: https://github.com/unblinkr/scout-polymarket ✅
- Vercel account (free tier works)

## Step-by-Step Vercel Deployment

### 1. Sign up / Log in to Vercel
Go to: https://vercel.com/signup

Choose "Continue with GitHub" — this will authorize Vercel to access your repos.

### 2. Import the Scout Project

Once logged in:
1. Click **"Add New..."** → **"Project"**
2. Find `scout-polymarket` in your repo list
3. Click **"Import"**

### 3. Configure the Project

Vercel will auto-detect it's a Python project. Configure:

**Framework Preset:** Other  
**Root Directory:** `./` (leave default)  
**Build Command:** (leave empty)  
**Output Directory:** (leave empty)

### 4. Add Environment Variables

Click **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `DISCORD_WEBHOOK_URL` | `https://discord.com/api/webhooks/1475955947074617354/Es0ui_Ya3d03Z-3cUFGkm4ylC-pi-PbKaUsASWgKjyuaf_vOXSsDounqTIWkd7Cfesmn` |

### 5. Deploy

Click **"Deploy"**

Vercel will:
- Install Python dependencies from `requirements.txt`
- Build your FastAPI app
- Deploy it to a public URL like `scout-polymarket.vercel.app`

This takes ~2-3 minutes.

### 6. Test Your Deployment

Once deployed, Vercel gives you a URL. Test it:

```bash
# Health check
curl https://scout-polymarket.vercel.app/

# Get markets
curl https://scout-polymarket.vercel.app/markets

# Detect arbitrage opportunities
curl https://scout-polymarket.vercel.app/arbitrage

# Send test alert to Discord
curl https://scout-polymarket.vercel.app/alert/arbitrage
```

### 7. Set Up Cron (Auto-Alerts)

The `vercel.json` already includes a cron job:
```json
"crons": [
  {
    "path": "/alert/arbitrage",
    "schedule": "*/5 * * * *"
  }
]
```

This will check for arbitrage opportunities **every 5 minutes** and alert Discord automatically.

**Note:** Cron jobs on Vercel's free tier may have limitations. If you need more frequent checks, upgrade to Pro ($20/mo) or use an external cron service like cron-job.org.

---

## What You'll Get

Once deployed:
- 🔍 **Real-time arbitrage detection** via Polymarket Gamma API
- 📊 **REST API** for querying markets and opportunities
- 🚨 **Discord alerts** every 5 minutes when arbitrage is detected
- 📈 **Scalable** — Vercel handles traffic spikes automatically

---

## Troubleshooting

**"Build failed":**
- Check that `requirements.txt` is in the root
- Verify Python version compatibility (Vercel uses 3.9+ by default)

**"Discord webhook not working":**
- Verify the webhook URL is correct in Environment Variables
- Test manually: `curl -X POST -H "Content-Type: application/json" -d '{"content": "test"}' YOUR_WEBHOOK_URL`

**"No arbitrage opportunities found":**
- This is normal if markets are efficient
- Try lowering `min_volume` parameter in `/arbitrage?min_volume=1000`

---

## Next Steps After Deployment

1. **Monitor Discord** — Wait for first arbitrage alert
2. **Add x402 Payments** — Monetize API access via micropayments
3. **Build Dashboard** — Simple React frontend to visualize opportunities
4. **Add More Features:**
   - ELI5 market explainer
   - Portfolio P&L tracker
   - Whale wallet alerts
   - Custom watchlists

Let's ship this. 🚀
