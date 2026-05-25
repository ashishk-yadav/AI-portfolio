# prompt_templates.py
SYS_TECH = "You are a precise technical writer. Follow the company API doc template strictly."
SYS_LEGAL = "You are a pragmatic legal drafter. Be clear, concise, and neutral. Prefer short clauses."

TEMPLATE = """<s>[SYSTEM]
{system}
[/SYSTEM]
[INSTRUCTION]
{instruction}
[/INSTRUCTION]
[INPUT]
{input}
[/INPUT]
[RESPONSE]
"""

def format_prompt(instruction: str, input_text: str = "", system: str = SYS_TECH) -> str:
    return TEMPLATE.format(system=system, instruction=instruction.strip(),
                           input=(input_text or "").strip())

def format_prompt_legal(instruction: str, input_text: str = "") -> str:
    return format_prompt(instruction, input_text, system=SYS_LEGAL)
