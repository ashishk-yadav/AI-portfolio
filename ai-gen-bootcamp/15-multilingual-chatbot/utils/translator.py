import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from llm_provider import get_llm_response, get_openai_compatible_client, active_provider, active_model

load_dotenv()


# -------- Google Translate (via deep-translator — no LLM key needed) --------
def google_translate(text: str, target_lang: str = "fr") -> str:
    """Uses deep-translator GoogleTranslator for baseline translation."""
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        return f"[Error: {e}]"


# -------- Prompt Styling Helper --------
def build_prompt(text: str, target_lang: str, style: str = "Default") -> str:
    if style == "Default":
        return f"Translate this into {target_lang}: {text}"
    elif style == "Formal":
        return f"Translate this into {target_lang} in a formal, business tone: {text}"
    elif style == "Casual":
        return f"Translate this into {target_lang} in a friendly and casual tone: {text}"
    elif style == "Slang":
        return f"Translate this into {target_lang} using slang/GenZ style: {text}"
    else:
        return f"Translate this into {target_lang}: {text}"


# -------- LLM Translation (all providers) --------
def gpt_translate(text: str, target_lang: str = "fr", style: str = "Default") -> str:
    """Translates using the currently selected LLM provider."""
    try:
        prompt = build_prompt(text, target_lang, style)
        return get_llm_response(
            messages=[
                {"role": "system", "content": "You are a helpful translation assistant."},
                {"role": "user", "content": prompt},
            ]
        )
    except Exception as e:
        return f"[Error: {e}]"


# -------- Streaming Translation (OpenAI/Groq only; Anthropic falls back to non-streaming) --------
def gpt_stream_translate(text: str, target_lang: str = "fr", style: str = "Default"):
    """Streams translation tokens. Falls back to non-streaming for Anthropic."""
    try:
        provider = active_provider()
        prompt = build_prompt(text, target_lang, style)
        if provider in ("OpenAI", "Groq"):
            client = get_openai_compatible_client()
            stream = client.chat.completions.create(
                model=active_model(),
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            # Anthropic: no streaming in this helper — yield full response at once
            yield get_llm_response(
                messages=[{"role": "user", "content": prompt}]
            )
    except Exception as e:
        yield f"[Error: {e}]"
