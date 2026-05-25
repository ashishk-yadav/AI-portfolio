from prompt_templates import format_prompt

SYS_MARKETING = "You are a sharp marketing copywriter. Be concise, on-brand, and punchy. Prefer strong verbs and clear CTAs."

def format_prompt_marketing(instruction: str, input_text: str = "") -> str:
    return format_prompt(instruction, input_text, system=SYS_MARKETING)
