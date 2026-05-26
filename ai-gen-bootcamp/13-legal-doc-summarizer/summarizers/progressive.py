import os
from dotenv import load_dotenv
from utils.chunking import token_chunks
from llm_provider import get_llm_response

load_dotenv()


def summarize(text):
    chunks = token_chunks(text)
    running_summary = ""
    for chunk in chunks:
        prompt = f"""You are summarizing a long document progressively.
Here is the summary so far:
{running_summary}

Here is the next part of the document:
{chunk}

Update the summary by integrating the new information.
Keep it concise, structured, and non-repetitive."""
        running_summary = get_llm_response(
            messages=[
                {"role": "system", "content": "You are a progressive summarizer."},
                {"role": "user", "content": prompt},
            ]
        )
    return running_summary
