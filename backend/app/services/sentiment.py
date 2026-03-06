from __future__ import annotations

import re
import httpx

POSITIVE = {"surge", "rally", "beat", "growth", "bull", "optimism", "record", "up"}
NEGATIVE = {"crash", "drop", "lawsuit", "fraud", "bear", "fear", "down", "recession"}


class SentimentService:
    async def fetch_financial_headlines(self) -> list[str]:
        urls = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
        ]
        headlines: list[str] = []
        async with httpx.AsyncClient(timeout=12) as client:
            for url in urls:
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    headlines += re.findall(r"<title>(.*?)</title>", resp.text)[:25]
                except Exception:
                    continue
        return [h for h in headlines if h and "CDATA" not in h][:30]

    async def score_market_sentiment(self) -> float:
        headlines = await self.fetch_financial_headlines()
        if not headlines:
            return 0.0

        score = 0
        total = 0
        for h in headlines:
            text = h.lower()
            for token in re.findall(r"[a-z]+", text):
                if token in POSITIVE:
                    score += 1
                    total += 1
                elif token in NEGATIVE:
                    score -= 1
                    total += 1
        if total == 0:
            return 0.0
        normalized = score / total
        return float(max(min(normalized, 1), -1))


sentiment_service = SentimentService()
