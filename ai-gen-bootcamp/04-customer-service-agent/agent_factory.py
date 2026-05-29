import streamlit as st
from customer_support_agent import load_support_docs, build_retriever, SupportAgent


def get_user_agent(username, orders):
    # Build retriever once per session — cached in session_state to avoid
    # chromadb EphemeralClient re-initialisation bug (chromadb 0.5.x)
    if "retriever" not in st.session_state:
        support_docs = load_support_docs("docs")
        st.session_state.retriever = build_retriever(support_docs)

    if "user_agents" not in st.session_state:
        st.session_state.user_agents = {}

    if username not in st.session_state.user_agents:
        st.session_state.user_agents[username] = SupportAgent(
            st.session_state.retriever, orders
        )
    return st.session_state.user_agents[username]
