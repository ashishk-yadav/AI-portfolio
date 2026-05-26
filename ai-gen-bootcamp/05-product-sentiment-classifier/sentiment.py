import os
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()


def analyze_sentiment(reviews):
    prompt = (
        "Classify the overall sentiment of these product reviews as 'positive', 'neutral', or 'negative'. "
        "Just give one word answer along with relevant emoji icon.\n"
        + "\n".join(reviews)
    )
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    ).strip().lower()


def analyze_sentiments_per_review(reviews):
    out = []
    for review in reviews:
        prompt = (
            "Classify the sentiment of this product review as 'positive', 'neutral', or 'negative'. "
            f"Just give one word answer along with relevant emoji icon.\n{review}"
        )
        result = get_llm_response(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        out.append(result.strip().lower())
    return out
