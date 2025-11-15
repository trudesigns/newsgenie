import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env


class Settings:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.news_api_key = os.getenv("NEWS_API_KEY", "")
        self.search_api_key = os.getenv("SEARCH_API_KEY", "")  # optional

        # Example base URLs (you can swap for the real provider you use)
        # For a real project, you might use something like:
        #   - NewsAPI.org
        #   - GNews
        #   - Serper / SerpAPI / Tavily for search
        self.news_api_base_url = os.getenv(
            "NEWS_API_BASE_URL",
            "https://newsapi.org/v2/top-headlines",
        )
        self.web_search_base_url = os.getenv(
            "WEB_SEARCH_BASE_URL",
            "https://api.example-search.com/v1/search",
        )

        if not self.openai_api_key:
            print(
                "[WARN] OPENAI_API_KEY is not set. LLM calls will fail until you add it.")
        if not self.news_api_key:
            print("[WARN] NEWS_API_KEY is not set. News API calls will use MOCK data.")
        if not self.search_api_key:
            print("[INFO] SEARCH_API_KEY is not set. Web search will use MOCK data.")


settings = Settings()
