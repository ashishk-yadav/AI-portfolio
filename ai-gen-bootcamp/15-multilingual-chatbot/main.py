import os
import streamlit as st
from dotenv import load_dotenv
from langdetect import detect
from fpdf import FPDF

load_dotenv()

st.set_page_config(page_title="🌍 Multi-Language Chat Bot", layout="wide")

def _require_keys(*pairs):
    needed = [(k, lbl, ph) for k, lbl, ph in pairs if not os.getenv(k)]
    if not needed:
        return
    with st.sidebar:
        st.markdown("---")
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

from utils.tokenizer import simple_tokenize
from utils.translator import google_translate, gpt_translate, gpt_stream_translate

st.title("💬 Multi-Language Chat Translation Bot")
st.write("Chat in different languages with real-time translation + smart features!")

# Store chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []  # each message = {"sender": "UserA", "text": "...", "detected_lang": "...", "translated": "..."}

# Sidebar settings
st.sidebar.header("⚙️ Settings")
lang_userA = st.sidebar.selectbox("🌐 User A Preferred Language:", ["en", "fr", "es", "hi", "de", "zh-cn"], index=0)
lang_userB = st.sidebar.selectbox("🌐 User B Preferred Language:", ["en", "fr", "es", "hi", "de", "zh-cn"], index=2)
engine = st.sidebar.radio("Translation Engine:", ["Google Translate", "GPT-4o-mini", "GPT-4o-mini (Streaming)"])
style = st.sidebar.radio("Translation Style (GPT only):", ["Default", "Formal", "Casual", "Slang"])

# Translation wrapper
def translate_message(msg, target_lang):
    if engine == "Google Translate":
        return google_translate(msg, target_lang)
    elif engine == "GPT-4o-mini":
        return gpt_translate(msg, target_lang, style)
    else:  # Streaming
        return "".join([chunk for chunk in gpt_stream_translate(msg, target_lang, style)])

# Display chat history
st.markdown("### 🗨️ Chat History")
for msg in st.session_state.messages:
    if msg["sender"] == "UserA":
        st.markdown(f"🟦 **User A** ({msg['detected_lang']}) → ({lang_userB})")
        st.write(f"Original: {msg['text']}")
        st.success(f"Translated: {msg['translated']}")
        st.caption(f"Tokens: {simple_tokenize(msg['text'])}")
    else:
        st.markdown(f"🟩 **User B** ({msg['detected_lang']}) → ({lang_userA})")
        st.write(f"Original: {msg['text']}")
        st.success(f"Translated: {msg['translated']}")
        st.caption(f"Tokens: {simple_tokenize(msg['text'])}")

st.markdown("---")

# Input areas
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟦 User A")
    msg_a = st.text_input("Type message (User A):", key="input_a")
    if st.button("Send (User A)"):
        if msg_a.strip():
            detected_lang = detect(msg_a)
            translated = translate_message(msg_a, lang_userB)
            st.session_state.messages.append(
                {"sender": "UserA", "text": msg_a, "detected_lang": detected_lang, "translated": translated}
            )
            st.rerun()

with col2:
    st.subheader("🟩 User B")
    msg_b = st.text_input("Type message (User B):", key="input_b")
    if st.button("Send (User B)"):
        if msg_b.strip():
            detected_lang = detect(msg_b)
            translated = translate_message(msg_b, lang_userA)
            st.session_state.messages.append(
                {"sender": "UserB", "text": msg_b, "detected_lang": detected_lang, "translated": translated}
            )
            st.rerun()

# --- Export Functions ---
def export_markdown():
    chat_md = "# Chat Transcript\n\n"
    for msg in st.session_state.messages:
        chat_md += f"**{msg['sender']} ({msg['detected_lang']}):** {msg['text']}\n\n"
        chat_md += f"→ Translated: {msg['translated']}\n\n"
    return chat_md

def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Chat Transcript", ln=True, align="C")
    for msg in st.session_state.messages:
        pdf.multi_cell(0, 10, f"{msg['sender']} ({msg['detected_lang']}): {msg['text']}")
        pdf.multi_cell(0, 10, f"→ Translated: {msg['translated']}\n")
    return pdf

import io
from pypdf import PdfReader
from utils.translator import google_translate, gpt_translate

# --- Document Translation Section ---
st.markdown("## 📄 Document Translator")

uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
doc_target_lang = st.selectbox("Translate document into:", ["en", "fr", "es", "hi", "de", "zh-cn"], index=1)
doc_engine = st.radio("Engine for document translation:", ["Google Translate", "GPT-4o-mini"], horizontal=True)

if uploaded_file is not None:
    # Read file content
    if uploaded_file.type == "text/plain":
        content = uploaded_file.read().decode("utf-8").splitlines()
    else:  # PDF
        pdf = PdfReader(uploaded_file)
        content = []
        for page in pdf.pages:
            content.extend(page.extract_text().splitlines())

    st.write("### Original Document")
    st.text("\n".join(content[:20]) + ("\n... (truncated)" if len(content) > 20 else ""))

    # Translate line by line
    translated_lines = []
    with st.spinner("Translating document..."):
        for line in content:
            if line.strip():
                if doc_engine == "Google Translate":
                    translated_lines.append(google_translate(line, doc_target_lang))
                else:
                    translated_lines.append(gpt_translate(line, doc_target_lang))
            else:
                translated_lines.append("")

    # Show translated text
    st.write("### Translated Document")
    st.text("\n".join(translated_lines[:20]) + ("\n... (truncated)" if len(translated_lines) > 20 else ""))

    # Export as .txt
    translated_text = "\n".join(translated_lines)
    st.download_button(
        label="💾 Download Translated Document",
        data=translated_text.encode("utf-8"),
        file_name=f"translated_{doc_target_lang}.txt",
        mime="text/plain",
    )

# Export buttons
st.sidebar.markdown("### 📤 Export Options")
if st.sidebar.button("Export as Markdown"):
    md = export_markdown()
    st.sidebar.download_button("Download Transcript.md", md, "chat_transcript.md")
