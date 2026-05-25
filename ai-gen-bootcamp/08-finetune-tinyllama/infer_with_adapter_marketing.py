import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from prompt_template_marketing import format_prompt_marketing

MODEL_ID     = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
ADAPTER_DIR  = os.environ.get("ADAPTER_DIR", "outputs/tinyllama-marketing-lora/adapter")

if torch.cuda.is_available():
    DEVICE = "cuda"
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

def generate_marketing(instruction: str, input_text: str, max_new_tokens=180):
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE).eval()
    model = PeftModel.from_pretrained(base, ADAPTER_DIR).to(DEVICE).eval()

    prompt = format_prompt_marketing(instruction, input_text)
    ids = tok(prompt, return_tensors="pt")
    ids = {k: v.to(DEVICE) for k, v in ids.items()}

    with torch.no_grad():
        out = model.generate(
            **ids,
            max_new_tokens=max_new_tokens,
            do_sample=True, temperature=0.8, top_p=0.9,
            pad_token_id=tok.eos_token_id,
        )
    text = tok.decode(out[0], skip_special_tokens=True)
    return text.split("[RESPONSE]")[-1].strip()

if __name__ == "__main__":
    # Example: short landing hero
    instruction = "Draft a landing page hero section."
    input_text = "Product: PixLift background remover; Audience: marketers; Proof: used by 5k+ brands"
    print("\n=== AFTER FINE-TUNE (MARKETING LoRA adapter) ===")
    print(generate_marketing(instruction, input_text))
