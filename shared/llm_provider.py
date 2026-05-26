"""
llm_provider.py  —  Provider-agnostic LLM helper for Streamlit demos.

USAGE
-----
1. Copy this file into the project directory that needs LLM support.
2. Call provider_sidebar() once at app startup (after st.set_page_config).
3. In helper modules, call get_openai_compatible_client() or get_llm_response()
   instead of creating an OpenAI() client directly.

SUPPORTED PROVIDERS
-------------------
• OpenAI    — gpt-4o-mini, gpt-4o
• Groq      — llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
• Anthropic — claude-3-5-haiku-20241022, claude-3-5-sonnet-20241022

ENV VARS SET BY provider_sidebar()
-----------------------------------
  LLM_PROVIDER   "OpenAI" | "Groq" | "Anthropic"
  LLM_API_KEY    the entered key
  LLM_MODEL      selected model name
  LLM_BASE_URL   openai-compatible base URL (empty for OpenAI, set for Groq)

  EMBED_API_KEY  set when needs_embeddings=True (always an OpenAI key)
  EMBED_MODEL    embedding model name
"""

import os
import streamlit as st

# ---------------------------------------------------------------------------
# Provider catalogue
# ---------------------------------------------------------------------------
PROVIDERS: dict = {
    "OpenAI": {
        "env_var": "OPENAI_API_KEY",
        "placeholder": "sk-...",
        "chat_models": ["gpt-4o-mini", "gpt-4o"],
        "default_model": "gpt-4o-mini",
        "openai_compatible": True,
        "base_url": None,
        "has_embeddings": True,
        "embedding_models": ["text-embedding-3-small", "text-embedding-3-large"],
        "default_embedding_model": "text-embedding-3-small",
    },
    "Groq": {
        "env_var": "GROQ_API_KEY",
        "placeholder": "gsk_...",
        "chat_models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
        "default_model": "llama-3.3-70b-versatile",
        "openai_compatible": True,
        "base_url": "https://api.groq.com/openai/v1",
        "has_embeddings": False,
    },
    "Anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "placeholder": "sk-ant-...",
        "chat_models": [
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022",
        ],
        "default_model": "claude-3-5-haiku-20241022",
        "openai_compatible": False,
        "has_embeddings": False,
    },
}


# ---------------------------------------------------------------------------
# Sidebar widget
# ---------------------------------------------------------------------------
def provider_sidebar(
    key_prefix: str = "llm",
    show_model: bool = True,
    needs_embeddings: bool = False,
) -> dict:
    """
    Renders the LLM Provider section in the Streamlit sidebar.

    Parameters
    ----------
    key_prefix       : unique prefix so multiple calls don't clash on widget keys.
    show_model       : whether to render a model-selection dropdown.
    needs_embeddings : if True, show a separate OpenAI embedding-key field when
                       the chosen provider has no native embeddings (Groq/Anthropic).

    Returns
    -------
    dict with keys:
        provider, api_key, model,
        embed_api_key, embed_model   (populated when needs_embeddings=True)
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 LLM Provider")

        provider = st.selectbox(
            "Choose provider",
            options=list(PROVIDERS.keys()),
            index=0,
            key=f"_{key_prefix}_provider",
        )
        cfg = PROVIDERS[provider]

        st.caption("Used for this session only — never stored.")
        existing = os.getenv(cfg["env_var"], "")
        typed = st.text_input(
            f"🔑 {provider} API Key",
            type="password",
            placeholder=cfg["placeholder"],
            key=f"_{key_prefix}_key",
        )
        if typed:
            os.environ[cfg["env_var"]] = typed
            existing = typed

        model = cfg["default_model"]
        if show_model:
            model = st.selectbox(
                "Model",
                options=cfg["chat_models"],
                index=0,
                key=f"_{key_prefix}_model",
            )

        # --- Embedding subsection (RAG / vector-search apps) ---
        embed_api_key = ""
        embed_model = ""

        if needs_embeddings:
            if cfg["has_embeddings"]:
                # OpenAI: same key used for both chat and embeddings
                embed_api_key = existing or os.getenv("OPENAI_API_KEY", "")
                embed_model = st.selectbox(
                    "Embedding model",
                    options=PROVIDERS["OpenAI"]["embedding_models"],
                    index=0,
                    key=f"_{key_prefix}_embed_model",
                )
            else:
                # Groq / Anthropic: no native embeddings → need a separate OpenAI key
                st.markdown("#### 🔢 Embeddings (OpenAI)")
                st.caption(
                    f"{provider} doesn't provide embeddings. "
                    "Enter an OpenAI key to power the vector store."
                )
                ek_existing = os.getenv("OPENAI_API_KEY", "")
                ek_typed = st.text_input(
                    "OpenAI API Key (embeddings only)",
                    type="password",
                    placeholder="sk-...",
                    key=f"_{key_prefix}_embed_key",
                )
                if ek_typed:
                    os.environ["OPENAI_API_KEY"] = ek_typed
                    ek_existing = ek_typed
                embed_api_key = ek_existing
                embed_model = PROVIDERS["OpenAI"]["default_embedding_model"]

    # --- Gate: stop if keys are missing ---
    missing = []
    if not os.getenv(cfg["env_var"]):
        missing.append(f"{provider} API Key")
    if needs_embeddings and not cfg["has_embeddings"] and not os.getenv("OPENAI_API_KEY"):
        missing.append("OpenAI API Key (embeddings)")

    if missing:
        st.info(f"👈 Enter your {' and '.join(missing)} in the sidebar to run this demo.")
        st.stop()

    # Bridge: write unified env vars so helper modules can read them
    api_key = os.getenv(cfg["env_var"], "")
    os.environ["LLM_PROVIDER"] = provider
    os.environ["LLM_API_KEY"] = api_key
    os.environ["LLM_MODEL"] = model
    os.environ["LLM_BASE_URL"] = cfg.get("base_url") or ""
    if needs_embeddings:
        os.environ["EMBED_API_KEY"] = embed_api_key
        os.environ["EMBED_MODEL"] = embed_model

    return {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "embed_api_key": embed_api_key,
        "embed_model": embed_model,
    }


# ---------------------------------------------------------------------------
# LLM factory helpers  (called from helper modules or inline in app.py)
# ---------------------------------------------------------------------------

def get_openai_compatible_client():
    """
    Returns an ``openai.OpenAI`` client configured for the active provider.
    Works for OpenAI and Groq (both expose an OpenAI-compatible REST API).
    Raises ValueError if the active provider is Anthropic — use
    ``get_llm_response()`` or ``get_langchain_llm()`` instead.
    """
    from openai import OpenAI

    provider = os.getenv("LLM_PROVIDER", "OpenAI")
    if provider == "Anthropic":
        raise ValueError(
            "Anthropic is not OpenAI-compatible. "
            "Use get_llm_response() or get_langchain_llm() instead."
        )
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL") or None
    return OpenAI(api_key=api_key, **({"base_url": base_url} if base_url else {}))


def get_llm_response(messages: list, temperature: float = 0.0) -> str:
    """
    Universal chat-completion helper — works for OpenAI, Groq, and Anthropic.

    Parameters
    ----------
    messages    : list of dicts [{"role": "system"|"user"|"assistant", "content": "..."}]
    temperature : sampling temperature

    Returns
    -------
    The assistant's reply as a plain string.
    """
    provider = os.getenv("LLM_PROVIDER", "OpenAI")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if provider in ("OpenAI", "Groq"):
        client = get_openai_compatible_client()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    elif provider == "Anthropic":
        import anthropic

        system_content = next(
            (m["content"] for m in messages if m["role"] == "system"), None
        )
        user_msgs = [m for m in messages if m["role"] != "system"]
        client = anthropic.Anthropic(api_key=api_key)
        kwargs: dict = {
            "model": model,
            "max_tokens": 4096,
            "messages": user_msgs,
            "temperature": temperature,
        }
        if system_content:
            kwargs["system"] = system_content
        resp = client.messages.create(**kwargs)
        return resp.content[0].text or ""

    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_langchain_llm(temperature: float = 0.0):
    """
    Returns a LangChain ``BaseLanguageModel`` for the active provider.
    Requires langchain-openai, langchain-groq, langchain-anthropic in requirements.
    """
    provider = os.getenv("LLM_PROVIDER", "OpenAI")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if provider == "OpenAI":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
    elif provider == "Groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, temperature=temperature, groq_api_key=api_key)
    elif provider == "Anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, temperature=temperature, api_key=api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_langchain_embeddings():
    """
    Returns ``OpenAIEmbeddings`` using EMBED_API_KEY / EMBED_MODEL env vars.
    Only OpenAI is supported for embeddings (Groq/Anthropic have no embedding API).
    """
    from langchain_openai import OpenAIEmbeddings

    api_key = os.getenv("EMBED_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model, api_key=api_key)


def active_model() -> str:
    """Returns the currently selected model name."""
    return os.getenv("LLM_MODEL", "gpt-4o-mini")


def active_provider() -> str:
    """Returns the currently selected provider name."""
    return os.getenv("LLM_PROVIDER", "OpenAI")
