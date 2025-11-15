from typing import List, Dict, Optional, Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage  # <-- fixed import

from .config import settings


# Base LLM configuration
llm = ChatOpenAI(
    model="gpt-4o-mini",  # change to any model your account supports
    temperature=0.2,
    openai_api_key=settings.openai_api_key,
)


SYSTEM_PROMPT = """
You are NewsGenie, an AI-powered information and news assistant.

Goals:
1. Answer general knowledge and informational questions clearly and concisely.
2. Help users stay updated with reliable, up-to-date news.
3. Always distinguish between:
   - verified news,
   - your own explanation/summary,
   - and uncertainty when sources are unclear.

Guidelines:
- If the user asks for "latest" or "today" news, prefer calling the news tool.
- If the question is conceptual (e.g. "explain inflation"), focus on explanation.
- If both news and explanation are needed, you may combine them.
- Be honest about limitations and do not invent sources.
"""


def call_llm(messages: List[HumanMessage | SystemMessage]) -> str:
    """
    Helper to call the LLM with a list of messages.
    messages should be langchain_core.messages (SystemMessage, HumanMessage, etc.).
    """
    response = llm.invoke(messages)
    return response.content


def classify_query(user_query: str) -> Literal["news", "general"]:
    """
    Very simple rule-based classifier for now.
    We will keep it simple so the logic is easy to explain in the report.
    Later you could replace this with an LLM-based classifier if desired.
    """
    query_lower = user_query.lower()

    news_keywords = [
        "news",
        "headline",
        "headlines",
        "latest",
        "today",
        "market update",
        "stock market",
        "breaking",
        "technology news",
        "sports scores",
        "finance news",
    ]

    # If any news keyword appears, treat as news query
    if any(keyword in query_lower for keyword in news_keywords):
        return "news"

    # If user mentions a specific date and asks "what happened on"
    if "what happened" in query_lower:
        return "news"

    # Default to general informational question
    return "general"


def generate_general_answer(user_query: str, chat_history: List[Dict]) -> str:
    """
    Use the LLM to answer non-news questions, while considering chat history.
    """
    messages: List[HumanMessage | SystemMessage] = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    for turn in chat_history:
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        # You could also add assistant messages as AIMessage if desired.

    messages.append(HumanMessage(content=user_query))

    return call_llm(messages)


def summarize_news_items(
    news_items: List[Dict],
    user_query: str,
    category: Optional[str] = None,
) -> str:
    """
    Use the LLM to summarize a list of news items for the user.
    """
    if not news_items:
        return "I couldn't find any relevant news items right now."

    # Build a simple text representation of the news list
    news_text_lines = []
    for idx, item in enumerate(news_items, start=1):
        line = (
            f"{idx}. {item.get('title', 'Untitled')} "
            f"({item.get('source', 'Unknown source')}, "
            f"{item.get('published_at', 'unknown date')})\n"
            f"   {item.get('description', '')}\n"
            f"   Link: {item.get('url', '')}"
        )
        news_text_lines.append(line)

    news_block = "\n\n".join(news_text_lines)

    prompt = f"""
The user asked: {user_query}

You have the following news articles (title, source, date, description, link):

{news_block}

1. Provide a concise summary of the most important points.
2. Highlight any trends or patterns.
3. If appropriate, suggest what a typical user might want to watch out for.
4. Do NOT invent facts beyond what is implied by the articles.
"""

    messages: List[HumanMessage | SystemMessage] = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    return call_llm(messages)
