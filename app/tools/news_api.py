from typing import List, Dict, Optional
import httpx

from ..config import settings


def _mock_news(category: str) -> List[Dict]:
    """
    Fallback news when NEWS_API_KEY is missing.
    Useful for demos and for your Course project if you don't want to sign up for an API.
    """
    category = (category or "general").lower()

    if category == "technology":
        return [
            {
                "title": "AI Startups Transforming the Tech Landscape",
                "description": "A look at how AI-powered tools are reshaping software development and productivity.",
                "url": "https://example.com/ai-startups",
                "source": "Mock Tech Daily",
                "published_at": "2025-01-01T10:00:00Z",
            },
            {
                "title": "Breakthrough in Quantum Computing Announced",
                "description": "Researchers reveal a new quantum processor with improved stability.",
                "url": "https://example.com/quantum-breakthrough",
                "source": "Mock Science News",
                "published_at": "2025-01-01T09:30:00Z",
            },
        ]

    if category == "finance":
        return [
            {
                "title": "Global Markets Rally After Inflation Report",
                "description": "Stocks rise as inflation data comes in lower than expected.",
                "url": "https://example.com/markets-rally",
                "source": "Mock Finance Times",
                "published_at": "2025-01-01T11:15:00Z",
            },
            {
                "title": "Central Bank Signals Possible Rate Cuts",
                "description": "Investors react to hints of a shift in monetary policy.",
                "url": "https://example.com/rate-cuts",
                "source": "Mock Economic Review",
                "published_at": "2025-01-01T08:45:00Z",
            },
        ]

    if category == "sports":
        return [
            {
                "title": "Underdog Team Wins Championship in Overtime",
                "description": "A dramatic finish caps off an unforgettable season.",
                "url": "https://example.com/championship",
                "source": "Mock Sports Network",
                "published_at": "2025-01-01T07:00:00Z",
            },
            {
                "title": "Star Player Sets New Scoring Record",
                "description": "A historic performance cements the player's legacy.",
                "url": "https://example.com/scoring-record",
                "source": "Mock Sports Network",
                "published_at": "2025-01-01T06:30:00Z",
            },
        ]

    # general fallback
    return [
        {
            "title": "Global News Summary",
            "description": "A quick overview of major headlines around the world.",
            "url": "https://example.com/global-summary",
            "source": "Mock World News",
            "published_at": "2025-01-01T05:00:00Z",
        }
    ]


async def fetch_news_async(
    category: Optional[str] = None,
    query: Optional[str] = None,
    language: str = "en",
    page_size: int = 5,
) -> List[Dict]:
    """
    Fetch news using a real API if NEWS_API_KEY is set.
    Otherwise, return mock news items.
    This function is async so it integrates nicely if you later use async workflows.
    """
    if not settings.news_api_key:
        # Use mock data
        return _mock_news(category or "general")

    # Example: using NewsAPI.org-style endpoint
    params = {
        "apiKey": settings.news_api_key,
        "language": language,
        "pageSize": page_size,
    }

    if category:
        params["category"] = category
    if query:
        params["q"] = query

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.news_api_base_url, params=params)
            response.raise_for_status()
            data = response.json()

        articles = data.get("articles", [])
        results: List[Dict] = []

        for art in articles:
            results.append(
                {
                    "title": art.get("title", ""),
                    "description": art.get("description") or "",
                    "url": art.get("url") or "",
                    "source": (art.get("source") or {}).get("name", ""),
                    "published_at": art.get("publishedAt") or "",
                }
            )

        if not results:
            return _mock_news(category or "general")

        return results

    except Exception as e:
        print(f"[ERROR] fetch_news_async failed: {e}")
        # On error, use mock so UX is not broken
        return _mock_news(category or "general")
