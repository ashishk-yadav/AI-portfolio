import os
import numpy as np
from dotenv import load_dotenv
from utils.chunking import token_chunks
from utils.embeddings import embed_texts
from llm_provider import get_llm_response

load_dotenv()


def summarize(text, query=None):
    print("Inside RAG summarizer")
    chunks = token_chunks(text)
    vectors = embed_texts(chunks)
    if query:
        qvec = embed_texts([query])[0]
        sims = vectors @ (qvec / np.linalg.norm(qvec))
        idxs = np.argsort(sims)[::-1][:6]
        sel = [chunks[i] for i in idxs]
    else:
        sel = chunks
    ctx = "\n---\n".join(sel)
    prompt = f"Summarize context with citations if possible:\n{ctx}"
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You are an analyst summarizer."},
            {"role": "user", "content": prompt},
        ]
    )
