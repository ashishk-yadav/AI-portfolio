from openai import OpenAI
import os, json
from dotenv import load_dotenv

load_dotenv()
CHAT_MODEL = "gpt-4o-mini"

def generate(text: str) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        "Create metadata for a document. Return strict JSON with keys: "
        "title, tldr, linkedin_blurb, x_blurb. "
        "title: <= 80 chars; tldr: one sentence <= 25 words; "
        "linkedin_blurb: 2-3 sentences, professional tone; "
        "x_blurb: <= 280 chars, punchy.\n\n"
        f"Document:\n{text[:16000]}"
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role":"system","content":"You produce concise, catchy titles and blurbs in strict JSON."},
            {"role":"user","content":prompt}
        ]
    )
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except Exception:
        # Fallback: return plain dict with raw text under tldr
        return {"title":"", "tldr":raw.strip(), "linkedin_blurb":"", "x_blurb":""}
