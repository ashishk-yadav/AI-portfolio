# prompt_templates.py
SYS = "You are a precise technical writer. Follow the company API doc template strictly."
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

def format_prompt(instruction: str, input_text: str = "", system: str = SYS) -> str:
    return TEMPLATE.format(system=system, instruction=instruction.strip(),
                           input=(input_text or "").strip())
