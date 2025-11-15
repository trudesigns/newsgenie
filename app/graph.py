from typing import TypedDict, Literal, List, Optional
import asyncio  # <-- new

from langgraph.graph import StateGraph, START, END

from .agents import (
    classify_query,
    generate_general_answer,
    summarize_news_items,  # <-- make sure this exists in agents.py
)
from .tools.news_api import fetch_news_async
from .tools.web_search import search_web_async


# 1. Define the graph state

class NewsItem(TypedDict, total=False):
    title: str
    description: str
    url: str
    source: str
    published_at: str


class GraphState(TypedDict, total=False):
    user_query: str
    query_type: Literal["news", "general"]
    # [{"role": "user"/"assistant", "content": "..."}]
    chat_history: List[dict]
    # "technology", "finance", "sports", etc.
    news_category: Optional[str]
    news_results: List[NewsItem]
    final_answer: str
    error: Optional[str]


# 2. Node functions

def classify_node(state: GraphState) -> GraphState:
    """
    Decide whether the user query is a news query or a general informational query.
    """
    query = state.get("user_query", "")
    qtype = classify_query(query)
    state["query_type"] = qtype
    return state


def news_node(state: GraphState) -> GraphState:
    """
    Handle news-related queries:
    - Fetch category-specific news.
    - Optionally use web search as a fallback or complement.
    - Summarize using the LLM.
    """
    user_query = state.get("user_query", "")
    chat_history = state.get("chat_history", []) or []
    category = (state.get("news_category") or "").lower()

    # If UI didn't specify a category, try to infer a simple one from the query
    if not category:
        q_lower = user_query.lower()
        if "tech" in q_lower or "ai" in q_lower or "software" in q_lower:
            category = "technology"
        elif "stock" in q_lower or "market" in q_lower or "finance" in q_lower:
            category = "finance"
        elif "sport" in q_lower or "game" in q_lower or "score" in q_lower:
            category = "sports"
        else:
            category = "general"

    try:
        # Call async tools from sync code
        news_items = asyncio.run(
            fetch_news_async(category=category, query=user_query)
        )

        # Optional: also call web search (not strictly required for every query)
        # For now, we won't merge them into the summary to keep it simple.
        _ = asyncio.run(
            search_web_async(query=user_query, num_results=2)
        )

        state["news_results"] = news_items

        summary = summarize_news_items(
            news_items, user_query, category=category)
        state["final_answer"] = summary

        # Update chat history
        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": summary})
        state["chat_history"] = chat_history

    except Exception as e:
        error_msg = f"Sorry, I had trouble fetching news right now. Error: {e}"
        state["error"] = str(e)
        state["final_answer"] = error_msg

        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": error_msg})
        state["chat_history"] = chat_history

    return state


def general_node(state: GraphState) -> GraphState:
    """
    Handle general informational questions using the LLM.
    """
    user_query = state.get("user_query", "")
    chat_history = state.get("chat_history", [])

    answer = generate_general_answer(user_query, chat_history)
    state["final_answer"] = answer

    # Update chat_history for future turns
    chat_history.append({"role": "user", "content": user_query})
    chat_history.append({"role": "assistant", "content": answer})
    state["chat_history"] = chat_history

    return state


def final_node(state: GraphState) -> GraphState:
    """
    Final node to possibly post-process output, log, or enforce formatting.
    Right now, we simply return the state as is.
    """
    return state


# 3. Build the graph

def build_graph():
    graph = StateGraph(GraphState)

    # Register nodes
    graph.add_node("classify", classify_node)
    graph.add_node("news", news_node)
    graph.add_node("general", general_node)
    graph.add_node("final", final_node)

    # Edges
    graph.add_edge(START, "classify")

    # Conditional edge: route based on query_type
    def route_based_on_type(state: GraphState) -> str:
        qtype = state.get("query_type", "general")
        if qtype == "news":
            return "news"
        return "general"

    graph.add_conditional_edges(
        "classify",
        route_based_on_type,
        {
            "news": "news",
            "general": "general",
        },
    )

    # From both main branches to final
    graph.add_edge("news", "final")
    graph.add_edge("general", "final")

    graph.add_edge("final", END)

    return graph.compile()
