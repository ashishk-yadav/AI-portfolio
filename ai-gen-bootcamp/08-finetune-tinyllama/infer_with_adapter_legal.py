import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from legal_prompt_template import format_prompt_legal

MODEL_ID    = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
ADAPTER_DIR = os.environ.get("ADAPTER_DIR", "outputs/tinyllama-legal-lora/adapter")

if torch.cuda.is_available():
    DEVICE = "cuda"
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

def generate_legal(instruction: str, input_text: str, max_new_tokens=220):
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE).eval()
    model = PeftModel.from_pretrained(base, ADAPTER_DIR).to(DEVICE).eval()

    prompt = format_prompt_legal(instruction, input_text)
    ids = tok(prompt, return_tensors="pt")
    ids = {k: v.to(DEVICE) for k, v in ids.items()}
    with torch.no_grad():
        out = model.generate(
            **ids, max_new_tokens=max_new_tokens,
            do_sample=True, temperature=0.7, top_p=0.9,
            pad_token_id=tok.eos_token_id
        )
    text = tok.decode(out[0], skip_special_tokens=True)
    return text.split("[RESPONSE]")[-1].strip()

if __name__ == "__main__":
    # Try a realistic prompt
    instruction = "Draft a Limitation of Liability clause."
    input_text = "Cap: fees paid in prior 12 months; Exclude indirect damages; Carve-out: breach of confidentiality and IP infringement."
    print("\n=== AFTER FINE-TUNE (LEGAL LoRA adapter) ===")
    print(generate_legal(instruction, input_text))
