import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="LLM Setup & Provider Comparison", page_icon="⚡", layout="wide")


def get_keys():
    openai_key = os.getenv("OPENAI_API_KEY")
    hf_token   = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    missing_openai = not openai_key
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        if missing_openai:
            val = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
            if val:
                os.environ["OPENAI_API_KEY"] = val
                openai_key = val
        hf_val = st.text_input("HuggingFace Token (optional)", type="password", placeholder="hf_...")
        if hf_val:
            os.environ["HF_TOKEN"] = hf_val
            hf_token = hf_val
        if not os.getenv("OPENAI_API_KEY"):
            st.warning("OpenAI key required to run the live comparison.")
    if not os.getenv("OPENAI_API_KEY"):
        st.info("Add your OpenAI API Key in the sidebar to run the live provider demo.\n\nGet one at [platform.openai.com](https://platform.openai.com).")
        st.stop()
    return os.getenv("OPENAI_API_KEY"), os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")


def call_openai(prompt: str, api_key: str, model: str = "gpt-4o-mini") -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content


def call_hf(prompt: str, token: str) -> str:
    from huggingface_hub import InferenceClient
    client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=token)
    messages = [{"role": "user", "content": prompt}]
    response = client.chat_completion(messages=messages, max_tokens=300)
    return response.choices[0].message.content


st.title("⚡ LLM Setup & Provider Comparison")
st.caption("Side-by-side comparison of OpenAI (cloud API), HuggingFace Hub (open-source), and Ollama (local) — integrating all three in one session.")

openai_key, hf_token = get_keys()

st.markdown("---")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown("#### Live Provider Comparison")
    prompt = st.text_area(
        "Enter a prompt to test across providers:",
        value="Explain the difference between fine-tuning and RAG for enterprise AI in 3 bullet points.",
        height=100,
    )

    providers = st.multiselect(
        "Select providers to compare",
        ["OpenAI GPT-4o-mini", "HuggingFace Mistral-7B"],
        default=["OpenAI GPT-4o-mini"],
    )

    if st.button("Run Comparison", type="primary", use_container_width=True):
        if not providers:
            st.warning("Select at least one provider.")
        else:
            cols = st.columns(len(providers))
            for i, provider in enumerate(providers):
                with cols[i]:
                    st.markdown(f"**{provider}**")
                    with st.spinner(f"Calling {provider}…"):
                        try:
                            if provider == "OpenAI GPT-4o-mini":
                                result = call_openai(prompt, openai_key)
                            elif provider == "HuggingFace Mistral-7B":
                                if not hf_token:
                                    st.warning("Add HuggingFace Token in sidebar.")
                                    continue
                                result = call_hf(prompt, hf_token)
                            st.info(result)
                        except Exception as e:
                            st.error(f"Error: {e}")

with col2:
    st.markdown("#### Provider Tradeoffs")
    st.markdown("""
| | OpenAI | HuggingFace | Ollama |
|--|--|--|--|
| **Privacy** | Cloud | Cloud | Local |
| **Cost** | Per token | Free tier | Free |
| **Latency** | ~500ms | ~2–5s | ~1–3s |
| **Model quality** | Highest | High | Varies |
| **Fine-tuning** | API | Full access | Full access |
    """)

    st.markdown("#### Ollama (local)")
    st.code("""# Run LLMs locally — no API key
ollama pull llama3.2
ollama run llama3.2

# Python integration
import ollama
response = ollama.chat(
    model='llama3.2',
    messages=[{'role':'user',
               'content': prompt}]
)
print(response['message']['content'])""", language="python")
    st.caption("Ollama runs fully offline — ideal for sensitive enterprise data where cloud APIs are not permitted.")
