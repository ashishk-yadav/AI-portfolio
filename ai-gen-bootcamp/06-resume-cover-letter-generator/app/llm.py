import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()


@dataclass
class GenConfig:
    max_tokens: int = 600
    temperature: float = 0.1


def generate_text(prompt: str, cfg: Optional[GenConfig] = None) -> str:
    """
    Generates text using the currently selected LLM provider.
    Provider / key / model are read from env vars set by provider_sidebar().
    """
    cfg = cfg or GenConfig()
    return get_llm_response(
        messages=[{"role": "user", "content": prompt}],
        temperature=cfg.temperature,
    )
