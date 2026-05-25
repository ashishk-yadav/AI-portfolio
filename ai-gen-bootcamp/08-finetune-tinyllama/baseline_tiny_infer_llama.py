# baseline_infer_tinyllama.py
# ---
# Minimal, stable baseline generation for TinyLlama-1.1B-Chat-v1.0
# Uses the model's chat template + safer decoding settings
# Works on CPU, Apple Silicon (MPS), or NVIDIA GPU.

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Pick best available device
if torch.cuda.is_available():
    DEVICE, TORCH_DTYPE = "cuda", torch.float16
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    DEVICE, TORCH_DTYPE = "mps", torch.float16
else:
    DEVICE, TORCH_DTYPE = "cpu", None

def build_messages_api_doc(endpoint_block: str):
    """
    Build a simple two-turn chat: system + user.
    You can swap this builder for your own task later.
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a precise technical writer. Follow this API doc template strictly:\n"
                "Summary\nEndpoint\nParameters (markdown table)\nResponses\n"
                "Do not invent extra turns. Keep it concise and consistent."
            ),
        },
        {
            "role": "user",
            "content": f"Write an API doc page.\n{endpoint_block}",
        },
    ]

def generate_api_doc(endpoint_block: str, max_new_tokens: int = 320) -> str:
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=TORCH_DTYPE if TORCH_DTYPE is not None else None
    ).to(DEVICE).eval()

    # Use the model's chat template for stable formatting
    messages = build_messages_api_doc(endpoint_block)
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    # Generate with tighter, de-looped settings
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.5,         # lower = more structured
            top_p=0.9,
            repetition_penalty=1.1,  # discourages repeating tags/lines
            pad_token_id=tok.eos_token_id,
        )

    # --- Clean extraction: only new tokens after the prompt (no echo) ---
    generated_ids = out[0]
    prompt_len = inputs["input_ids"].shape[-1]
    new_tokens = generated_ids[prompt_len:]
    text = tok.decode(new_tokens, skip_special_tokens=True)

    # Light post-trim: stop if the model starts a new bracketed section
    # (keeps first coherent block; optional but helps with small models)
    cut_markers = ["\n[", "\n<System", "\nUser:", "\nAssistant:"]
    for m in cut_markers:
        if m in text:
            text = text.split(m, 1)[0]
    return text.strip()

if __name__ == "__main__":
    # Example baseline prompt (same one you used earlier)
    endpoint = (
        "Endpoint: POST /v1/refunds; Auth: Bearer token; "
        "Params: payment_id (string, required), amount (integer, optional); "
        "Response: 201 {refund}, 400, 401"
    )
    print("\n=== BASELINE (TinyLlama chat template) ===\n")
    print(generate_api_doc(endpoint))
