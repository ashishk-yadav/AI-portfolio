import os
import json
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()


def generate(text: str) -> dict:
    prompt = (
        "Create metadata for a document. Return strict JSON with keys: "
        "title, tldr, linkedin_blurb, x_blurb. "
        "title: <= 80 chars; tldr: one sentence <= 25 words; "
        "linkedin_blurb: 2-3 sentences, professional tone; "
        f"x_blurb: <= 280 chars, punchy.\n\nDocument:\n{text[:16000]}"
    )
    raw = get_llm_response(
        messages=[
            {"role": "system", "content": "You produce concise, catchy titles and blurbs in strict JSON."},
            {"role": "user", "content": prompt},
        ]
    )
    try:
        return json.loads(raw)
    except Exception:
        return {"title": "", "tldr": raw.strip(), "linkedin_blurb": "", "x_blurb": ""}
