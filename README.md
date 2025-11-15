🧞‍♂️ NewsGenie – AI-Powered Information & News Assistant
Built with Streamlit, LangChain, LangGraph & OpenAI

Designed by Tru Designs & ChatGPT

📌 Overview

NewsGenie is an intelligent agentic system that combines real-time news retrieval, conversational AI, and workflow orchestration.
It automatically determines whether a user is asking for general information or current news, retrieves the correct data, summarizes it, and replies in a clean, human-friendly format.

This project was built as part of the Purdue / Simplilearn AGS: Agentic Frameworks coursework.

🎯 Purpose

The goal of NewsGenie is to:

Provide accurate real-time news summaries

Deliver clear general knowledge explanations

Automatically classify queries into news or general knowledge

Demonstrate a clean, reproducible agentic workflow using LangGraph

Provide UI experience and conversation memory using Streamlit

✨ Key Features
🧠 Smart Query Classification

Detects whether the user is asking for news or a general explanation

Uses lightweight rule-based logic (upgradeable to an LLM classifier)

📰 Real-Time News Retrieval

Retrieves news by category:

Technology

Finance

Sports

General

Falls back to mock data if API keys are missing

(Optional later: DuckDuckGo search, Bing news, etc.)

🤖 Agentic Workflow with LangGraph

StateGraph handles:

Query classification

News retrieval

LLM summarization

Conversation history

Error handling

💬 Chat Interface (Streamlit)

Full conversation history display

News cards with:

Title

Source

Date

Summary

Link

Tru Designs-branded footer

🛡 Robust Fallbacks

If news API fails → uses mock data

If all tools fail → LLM explains and suggests alternatives

📂 Project Structure
newsgenie_project/
│
├── app/
│   ├── agents.py          # LLM logic and summarization
│   ├── graph.py           # LangGraph workflow (state machine)
│   ├── config.py          # Settings, environment variables
│   └── tools/
│       ├── news_api.py    # News retrieval tool
│       └── web_search.py  # Fallback search tool
│
├── app/ui/
│   └── streamlit_app.py   # Streamlit UI front-end
│
├── .gitignore
├── requirements.txt       # Python dependencies
├── README.md
└── Report.pdf             # Final coursework report (optional)

🔧 Tech Stack
Backend / Agents

🧩 LangGraph

🔗 LangChain

🤖 OpenAI (GPT-4o mini for cost efficiency)

Frontend

🎨 Streamlit

🖼 Styled UI + Tru Designs branding

News Data

Custom News API tool

Automatic mock data fallback

Deployment

GitHub version control

(Next Step) Vercel or Streamlit Cloud

🧠 How the Agent Works
1. User enters a message

Example:

“Explain inflation”

“Show me the latest tech news”

2. Classifier decides:
"news" or "general"

3. LangGraph Workflow
User Query
    ↓
Classify
    ↓
If News? → Run News API → Summarize → Respond
If General? → LLM Explanation → Respond

4. UI Displays Results

Conversation bubbles

News summary cards

Related articles

Errors or fallback notices

🚨 Error Handling & Fallback Logic
Error Type	System Behavior
No News API Key	Uses mock data
API Timeout	Shows fallback explanation
Empty results	LLM politely says “no current news found”
Unexpected error	Full traceback hidden, clean user message shown
