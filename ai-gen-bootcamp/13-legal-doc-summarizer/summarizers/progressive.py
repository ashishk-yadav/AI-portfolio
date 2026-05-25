from openai import OpenAI
from utils.chunking import token_chunks
import os
from dotenv import load_dotenv

load_dotenv()



def summarize(text):
    CHAT_MODEL = "gpt-4o-mini"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    chunks = token_chunks(text)
    running_summary = ""
    for chunk in chunks:
        prompt = f"""
You are summarizing a long document progressively.
Here is the summary so far:
{running_summary}

Here is the next part of the document:
{chunk}

Update the summary by integrating the new information.
Keep it concise, structured, and non-repetitive.
"""
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role":"system","content":"You are a progressive summarizer."},
                      {"role":"user","content":prompt}]
        )
        running_summary = resp.choices[0].message.content
    return running_summary
