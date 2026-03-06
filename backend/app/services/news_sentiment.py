from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings

POSITIVE = {"surge", "beat", "growth", "rally", "bullish", "upgrade", "record"}
NEGATIVE = {"drop", "miss", "decline", "selloff", "bearish", "downgrade", "risk"}


@dataclass
class NewsSentimentService:
    async def score(self, symbol: str) -> float:
        if settings.news_api_key:
            try:
                return await self._score_with_newsapi(symbol)
            except Exception:
                pass
        return 0.0

    async def _score_with_newsapi(self, symbol: str) -> float:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": symbol,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 25,
            "apiKey": settings.news_api_key,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url, params=params)
            res.raise_for_status()
            payload = res.json()

        titles = [a.get("title", "") for a in payload.get("articles", [])]
        if not titles:
            return 0.0

        score = 0
        for title in titles:
            text = title.lower()
            score += sum(1 for p in POSITIVE if p in text)
            score -= sum(1 for n in NEGATIVE if n in text)
        return max(-1.0, min(1.0, score / (len(titles) * 2)))
