import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from openai import OpenAI

load_dotenv()

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- Google Translate (baseline via deep-translator) --------
def google_translate(text: str, target_lang: str = "fr") -> str:
    """
    Uses deep-translator GoogleTranslator for translation.
    """
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

# -------- GPT-4o-mini Translation --------
def gpt_translate(text: str, target_lang: str = "fr", style: str = "Default") -> str:
    try:
        prompt = build_prompt(text, target_lang, style)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful translation assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Error: {e}]"

# -------- Streaming GPT Translation --------
def gpt_stream_translate(text: str, target_lang: str = "fr", style: str = "Default"):
    try:
        prompt = build_prompt(text, target_lang, style)
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"[Error: {e}]"
