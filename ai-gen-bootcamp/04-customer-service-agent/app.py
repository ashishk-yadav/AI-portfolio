# app.py

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config("AI Customer Support Demo", layout="centered")

def _require_keys(*pairs):
    needed = [(k, lbl, ph) for k, lbl, ph in pairs if not os.getenv(k)]
    if not needed:
        return
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        for k, lbl, ph in needed:
            val = st.text_input(lbl, type="password", placeholder=ph, key=f"_k_{k}")
            if val:
                os.environ[k] = val
    still = [lbl for k, lbl, _ in pairs if not os.getenv(k)]
    if still:
        st.info(f"👈 Enter your {' and '.join(still)} in the sidebar to run this demo.")
        st.stop()

_require_keys(("OPENAI_API_KEY", "OpenAI API Key", "sk-..."))

from user_data import get_user_profile
from pages import (
    login_page, profile_page,
    chat_page, history_page, orders_page, escalations_page
)
from persistence import load_user_db

def main_app():
    st.sidebar.title("Navigation")
    pages = ["Support Chat", "My Profile", "My Past Queries", "My Orders", "My Escalations", "Logout"]

    choice = st.sidebar.radio("Go to", pages)

    username = st.session_state["logged_in_user"]
    user = get_user_profile(username)
    if choice == "Support Chat":
        chat_page(username)
    elif choice == "My Profile":
        profile_page(user["profile"])
    elif choice == "My Past Queries":
        history_page(user["history"])
    elif choice == "My Orders":
        orders_page(username)
    elif choice == "My Escalations":
        escalations_page(username)
    elif choice == "Logout":
        del st.session_state["logged_in_user"]
        st.rerun()

def run():
    # ---- PERSISTENCE: Load user DB at startup ----
    if "user_db" not in st.session_state:
        st.session_state.user_db = load_user_db()
    if "logged_in_user" not in st.session_state:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    run()
