from openai import OpenAI
import os, json
from dotenv import load_dotenv

load_dotenv()
CHAT_MODEL = "gpt-4o-mini"

def extract(text: str) -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        "Extract key points and action items from the document. "
        "Return strict JSON with keys: key_points (list of strings), actions (list of objects with fields action, owner, deadline, priority). "
        "Use 'TBD' if unknown. Keep 5-10 key_points and up to 10 actions.\n\n"
        f"Document:\n{text[:16000]}"
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role":"system","content":"You extract structured key points and action items and return strict JSON."},
            {"role":"user","content":prompt}
        ]
    )
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except Exception:
        return {"key_points":[raw.strip()], "actions":[]}
