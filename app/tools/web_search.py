from typing import List, Dict
import httpx

from ..config import settings


def _mock_search(query: str) -> List[Dict]:
    """
    Fallback web search when SEARCH_API_KEY is missing.
    """
    return [
        {
            "title": f"Background information related to: {query}",
            "snippet": "This is a mock search result used when no real web search API is configured.",
            "url": "https://example.com/mock-search",
        }
    ]


async def search_web_async(query: str, num_results: int = 3) -> List[Dict]:
    """
    Call a web search API if configured; otherwise return mock results.
    """
    if not settings.search_api_key:
        return _mock_search(query)

    # This is a placeholder; you would adapt this to your actual search provider.
    params = {
        "api_key": settings.search_api_key,
        "q": query,
        "num": num_results,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.web_search_base_url, params=params)
            response.raise_for_status()
            data = response.json()

        # The shape of `data` will depend on the provider.
        # We'll assume it returns a list of results under "results".
        results_raw = data.get("results", [])
        results: List[Dict] = []

        for item in results_raw[:num_results]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("url", ""),
                }
            )

        if not results:
            return _mock_search(query)

        return results

    except Exception as e:
        print(f"[ERROR] search_web_async failed: {e}")
        return _mock_search(query)
