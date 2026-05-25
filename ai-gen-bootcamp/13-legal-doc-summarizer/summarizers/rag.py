from openai import OpenAI
import numpy as np
from utils.chunking import token_chunks
from utils.embeddings import embed_texts

import os
from dotenv import load_dotenv

load_dotenv()

def summarize(text, query=None):
    CHAT_MODEL = "gpt-4o-mini"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("Inside RAG summarizer")
    chunks = token_chunks(text)
    vectors = embed_texts(chunks)
    if query:
        qvec = embed_texts([query])[0]
        sims = vectors @ (qvec/np.linalg.norm(qvec))
        idxs = np.argsort(sims)[::-1][:6]
        sel = [chunks[i] for i in idxs]
    else:
        sel = chunks
    ctx = "\n---\n".join(sel)
    prompt = f"Summarize context with citations if possible:\n{ctx}"
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":"You are an analyst summarizer."},
                  {"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content
