import os
import json
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()


def extract(text: str) -> dict:
    prompt = (
        "Extract key points and action items from the document. "
        "Return strict JSON with keys: key_points (list of strings), "
        "actions (list of objects with fields action, owner, deadline, priority). "
        "Use 'TBD' if unknown. Keep 5-10 key_points and up to 10 actions.\n\n"
        f"Document:\n{text[:16000]}"
    )
    raw = get_llm_response(
        messages=[
            {"role": "system", "content": "You extract structured key points and action items and return strict JSON."},
            {"role": "user", "content": prompt},
        ]
    )
    try:
        return json.loads(raw)
    except Exception:
        return {"key_points": [raw.strip()], "actions": []}
