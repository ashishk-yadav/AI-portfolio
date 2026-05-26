import os
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()


def summarize_reviews(reviews):
    prompt = "Summarize these product reviews in 2-3 crisp bullet points:\n" + "\n".join(reviews)
    print("summarization prompt and reviews", prompt)
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    ).strip()
