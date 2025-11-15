import streamlit as st
from app.graph import build_graph

# --------------------------------------------------------
# Initialize graph and session state
# --------------------------------------------------------
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # [{"role": "...", "content": "..."}]

graph = st.session_state.graph

# --------------------------------------------------------
# Page config
# --------------------------------------------------------
st.set_page_config(
    page_title="NewsGenie – AI News Assistant",
    page_icon="🧞",
    layout="wide",
)

st.title("🧞‍♂️ NewsGenie – AI-Powered Information & News Assistant")
st.write(
    "Ask general questions or request the latest news. "
    "NewsGenie will automatically determine the correct response mode."
)

# --------------------------------------------------------
# Sidebar – news category
# --------------------------------------------------------
st.sidebar.header("News Options")
news_category = st.sidebar.selectbox(
    "Preferred news category:",
    ["auto-detect", "technology", "finance", "sports", "general"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Examples:\n"
    "- 'Explain inflation'\n"
    "- 'Show me the latest tech news'\n"
    "- 'Give me today's finance headlines'"
)

# --------------------------------------------------------
# Show chat history
# --------------------------------------------------------
st.subheader("Conversation")

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

# --------------------------------------------------------
# Chat input
# --------------------------------------------------------
user_input = st.chat_input("Ask something...")

if user_input:
    # Add user message to history & display
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    state = {
        "user_query": user_input,
        "chat_history": st.session_state.chat_history[:-1],
        "news_category": None if news_category == "auto-detect" else news_category,
    }

    try:
        # Spinner while the graph is running (nicer UX)
        with st.spinner("Thinking and fetching any relevant news..."):
            result_state = graph.invoke(state)

        answer = result_state.get("final_answer", "No answer generated.")
        news_items = result_state.get("news_results", [])
        error = result_state.get("error")

        # Update history from graph
        st.session_state.chat_history = result_state.get("chat_history", [])

        with st.chat_message("assistant"):
            st.markdown(answer)

            if news_items:
                st.markdown("### Related News Articles")
                for item in news_items:
                    st.markdown(f"**{item.get('title', 'Untitled')}**")

                    meta_parts = []
                    if item.get("source"):
                        meta_parts.append(item["source"])
                    if item.get("published_at"):
                        meta_parts.append(item["published_at"])
                    if meta_parts:
                        st.caption(" • ".join(meta_parts))

                    if item.get("description"):
                        st.write(item["description"])

                    if item.get("url"):
                        st.markdown(f"[Read more]({item['url']})")

                    st.markdown("---")

            if error:
                st.warning(
                    "Some data could not be fetched. Showing fallback results."
                )

    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"Unexpected error occurred: {e}")

# --------------------------------------------------------
# Branded Footer – Tru Designs
# --------------------------------------------------------
st.markdown(
    """
    <style>
        .trudesigns-footer {
            width: 100%;
            text-align: center;
            margin-top: 60px;
            padding: 20px 0;
            color: #ffffff;
            font-size: 15px;
            letter-spacing: 0.5px;
            opacity: 0.85;
        }

        .trudesigns-footer span {
            background: linear-gradient(90deg, #ff1493, #ff4fa3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        .trudesigns-footer small {
            display: block;
            margin-top: 6px;
            font-size: 12px;
            opacity: 0.6;
        }

        .footer-divider {
            width: 60%;
            margin: 50px auto 25px auto;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        }
    </style>

    <div class="footer-divider"></div>
    <div class="trudesigns-footer">
        Designed by <span>Tru Designs</span> & ChatGPT  
        <small>AI-Powered Creativity • 2025</small>
    </div>
    """,
    unsafe_allow_html=True,
)
