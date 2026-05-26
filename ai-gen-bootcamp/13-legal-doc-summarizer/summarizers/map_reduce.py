import os
from dotenv import load_dotenv
from utils.chunking import token_chunks
from llm_provider import get_llm_response

load_dotenv()


def summarize(text):
    chunks = token_chunks(text)
    partials = []
    for ch in chunks:
        partials.append(
            get_llm_response(
                messages=[
                    {"role": "system", "content": "Summarize a section."},
                    {"role": "user", "content": ch},
                ]
            )
        )
    bigtext = "\n".join(partials)
    return get_llm_response(
        messages=[
            {"role": "system", "content": "Combine summaries."},
            {"role": "user", "content": bigtext},
        ]
    )
