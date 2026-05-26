import os
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()


def summarize(text, words=250):
    prompt = f"Summarize in about {words} words:\n\n{text[:12000]}"
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You are a concise summarizer."},
            {"role": "user", "content": prompt},
        ]
    )
