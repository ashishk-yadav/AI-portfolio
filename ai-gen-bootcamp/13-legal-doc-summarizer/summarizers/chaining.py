from openai import OpenAI
from summarizers import baseline
import os
from dotenv import load_dotenv

load_dotenv()

def summarize(text):
    CHAT_MODEL = "gpt-4o-mini"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    initial = baseline.summarize(text, words=150)
    prompt = f"Refine and expand this summary into structured bullets with obligations, risks, next steps:\n{initial}"
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":"You refine summaries."},
                  {"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content
