# Provider-agnostic coding agent
from dotenv import load_dotenv
import os
from memory import retrieve_relevant_chunks
from llm_provider import get_llm_response

load_dotenv()

SYSTEM_PROMPT = """You are an expert coding assistant.
Use the retrieved code context and user history to help with code understanding,
editing, or answering questions. If you edit code, return only the code,
else give a clear, concise answer."""


def build_prompt(user_query, retrieved_chunks, history):
    context_section = "\n\n".join(
        [f"Context {i+1}:\n{chunk}" for i, (chunk, _) in enumerate(retrieved_chunks)]
    )
    history_section = "\n".join(
        [f"User: {q}\nAssistant: {a}" for q, a in history]
    )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Previous discussion:\n{history_section}\n\n"
        f"Retrieved project context:\n{context_section}\n\n"
        f"User's current question:\n{user_query}"
    )


def ask_agent(user_query, history, k=4, model=None):
    retrieved_chunks = retrieve_relevant_chunks(user_query, k=k)
    prompt = build_prompt(user_query, retrieved_chunks, history)
    answer = get_llm_response(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    return answer, retrieved_chunks


def extract_code_from_answer(answer):
    """Tries to extract code block from LLM answer. Returns (code, rest_of_answer)."""
    import re
    code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", answer, re.DOTALL)
    if code_blocks:
        code = code_blocks[0]
        non_code = answer.replace(f"```python\n{code}\n```", "")
        return code, non_code
    return None, answer
