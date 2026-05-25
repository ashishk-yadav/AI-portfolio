from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def summarize(text, words=250):
    prompt = f"Summarize in about {words} words:\n\n{text[:12000]}"
    CHAT_MODEL = "gpt-4o-mini"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":"You are a concise summarizer."},
                  {"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content
