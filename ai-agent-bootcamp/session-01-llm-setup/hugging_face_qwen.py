from dotenv import load_dotenv
load_dotenv()

import  torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

# Pick device & dtype
device = "cpu"
dtype = torch.float32

# Load the tokenizers
tok = AutoTokenizer.from_pretrained(model_name)

# Load the model
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype).to(device).eval()


messages = [
    {"role": "system", "content": "You are a helpful assistant that answers clearly and concisely."},
    {"role": "user",   "content": "Write a 50 word summary on ethics in AI."},
]

# 4) Build prompt via chat template, then tokenize to a mapping
prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=2048)
inputs = {k: v.to(device) for k, v in inputs.items()}

with torch.no_grad():
    out = model.generate(
        **inputs,
        max_new_tokens=128, # Maximum number of token in output
        eos_token_id=tok.eos_token_id,
        pad_token_id=tok.eos_token_id
    )

new_tokens = out[0, inputs["input_ids"].shape[1]:]
print(tok.decode(new_tokens, skip_special_tokens=True).strip())
