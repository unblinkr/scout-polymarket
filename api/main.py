from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import List, Optional
from pydantic import BaseModel
import asyncio
from datetime import datetime

app = FastAPI(title="Scout Agent", version="0.1.0")

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
GAMMA_API = "https://gamma-api.polymarket.com"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

class ArbitrageOpportunity(BaseModel):
    market_id: str
    event_title: str
    question: str
    yes_price: float
    no_price: float
    combined_price: float
    potential_profit: float
    volume_24h: float
    url: str
    detected_at: datetime

@app.get("/")
async def health():
    return {"status": "Scout Agent running", "version": "0.1.0"}

@app.get("/markets")
async def get_markets(limit: int = 20):
    """Get active markets from Gamma API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GAMMA_API}/events", params={"limit": limit, "active": "true"})
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Gamma API error")
        return resp.json()

@app.get("/arbitrage")
async def detect_arbitrage(min_volume: float = 10000.0) -> List[ArbitrageOpportunity]:
    """
    Detect arbitrage opportunities where Yes + No < $1.00.
    This indicates a market inefficiency that can be exploited.
    """
    async with httpx.AsyncClient() as client:
        # Get markets with volume
        resp = await client.get(
            f"{GAMMA_API}/events",
            params={"limit": 100, "active": "true", "order": "volume24hr"}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Gamma API error")
        
        data = resp.json()
        opportunities = []
        
        for event in data:
            for market in event.get("markets", []):
                # Parse prices
                try:
                    prices = eval(market.get("outcomePrices", "[]"))
                    if len(prices) >= 2:
                        yes_price = float(prices[0])
                        no_price = float(prices[1])
                        combined = yes_price + no_price
                        
                        # Arbitrage condition: Yes + No < 0.99 (accounting for fees)
                        if combined < 0.99:
                            volume = market.get("volume24hr", 0)
                            if volume >= min_volume:
                                opp = ArbitrageOpportunity(
                                    market_id=market["id"],
                                    event_title=event.get("title", "Unknown"),
                                    question=market.get("question", ""),
                                    yes_price=yes_price,
                                    no_price=no_price,
                                    combined_price=combined,
                                    potential_profit=1.0 - combined,
                                    volume_24h=volume,
                                    url=f"https://polymarket.com/event/{event.get('slug', '')}",
                                    detected_at=datetime.utcnow()
                                )
                                opportunities.append(opp)
                except (ValueError, SyntaxError):
                    continue
        
        return sorted(opportunities, key=lambda x: x.potential_profit, reverse=True)

@app.post("/alert")
async def send_alert(message: str):
    """Send alert to Discord."""
    if not DISCORD_WEBHOOK:
        raise HTTPException(status_code=500, detail="Discord webhook not configured")
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DISCORD_WEBHOOK,
            json={"content": message}
        )
        if resp.status_code not in [200, 204]:
            raise HTTPException(status_code=500, detail="Discord webhook failed")
        return {"status": "sent"}

@app.get("/alert/arbitrage")
async def alert_arbitrage():
    """Check for arbitrage and send Discord alert if found."""
    opportunities = await detect_arbitrage()
    
    if not opportunities:
        return {"status": "no_arbitrage", "count": 0}
    
    # Build alert message
    top = opportunities[0]
    message = f"""🚨 **ARBITRAGE DETECTED**

**{top.event_title}**
{top.question}

💰 **Prices:** Yes ${top.yes_price:.4f} | No ${top.no_price:.4f} | **Combined: ${top.combined_price:.4f}**
📊 **Potential Profit:** ${top.potential_profit:.4f} ({top.potential_profit*100:.2f}%)
📈 **24h Volume:** ${top.volume_24h:,.0f}

🔗 [Trade on Polymarket]({top.url})

_Found {len(opportunities)} opportunities. Run `/arbitrage` for full list._
"""
    
    await send_alert(message)
    return {"status": "alert_sent", "count": len(opportunities), "top_profit": top.potential_profit}
