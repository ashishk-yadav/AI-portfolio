from openai import OpenAI
from utils.chunking import token_chunks
import os
from dotenv import load_dotenv

load_dotenv()


def summarize(text):
    CHAT_MODEL = "gpt-4o-mini"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    chunks = token_chunks(text)
    partials=[]
    for ch in chunks:
        resp=client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role":"system","content":"Summarize a section."},
                      {"role":"user","content":ch}]
        )
        partials.append(resp.choices[0].message.content)
    bigtext="\n".join(partials)
    resp=client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":"Combine summaries."},
                  {"role":"user","content":bigtext}]
    )
    return resp.choices[0].message.content
