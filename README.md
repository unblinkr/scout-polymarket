# Scout Agent — Polymarket Intelligence

Real-time arbitrage detection and aftermarket intelligence for Polymarket.

## Architecture

- **Backend:** FastAPI (Python 3.11+)
- **Data:** Polymarket Gamma API (no auth required)
- **Alerts:** Discord webhook
- **Payments:** x402 micropayments for API access
- **Deployment:** Vercel Serverless

## Quick Start

```bash
# Clone
git clone https://github.com/unblinkr/scout.git
cd scout

# Install
pip install -r requirements.txt

# Run locally
uvicorn api.main:app --reload

# Deploy
vercel --prod
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check |
| `GET /markets` | List active markets |
| `GET /arbitrage` | Current arbitrage opportunities (Yes + No < $1.00) |
| `POST /alert` | Trigger Discord alert |

## Environment Variables

```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
X402_WALLET_ADDRESS=...
X402_RECEIVER_ADDRESS=...
```

## License

MIT — Vision 2030
