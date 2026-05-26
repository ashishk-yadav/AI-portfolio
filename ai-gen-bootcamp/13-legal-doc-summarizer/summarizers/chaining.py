import os
from dotenv import load_dotenv
from summarizers import baseline
from llm_provider import get_llm_response

load_dotenv()


def summarize(text):
    initial = baseline.summarize(text, words=150)
    prompt = (
        "Refine and expand this summary into structured bullets with "
        f"obligations, risks, next steps:\n{initial}"
    )
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You refine summaries."},
            {"role": "user", "content": prompt},
        ]
    )
