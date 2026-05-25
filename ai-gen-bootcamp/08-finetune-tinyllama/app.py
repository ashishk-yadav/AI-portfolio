import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Fine-Tune TinyLlama (QLoRA)", page_icon="🦙", layout="wide")


def get_hf_token():
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if token:
        return token
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        val = st.text_input("HuggingFace Token", type="password", placeholder="hf_...")
        if val:
            os.environ["HF_TOKEN"] = val
    if not (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")):
        st.info("Add your HuggingFace Token in the sidebar to run live inference.\n\nGet one free at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).")
        st.stop()
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")


def run_inference(prompt: str, token: str) -> str:
    from huggingface_hub import InferenceClient
    client = InferenceClient(model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", token=token)
    messages = [{"role": "user", "content": prompt}]
    response = client.chat_completion(messages=messages, max_tokens=350)
    return response.choices[0].message.content


st.title("🦙 Fine-Tune TinyLlama-1.1B with QLoRA")
st.caption("Domain adaptation via LoRA/PEFT — run live inference on the base model and explore what fine-tuning changes.")

token = get_hf_token()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### How QLoRA Works")
    st.markdown("""
**LoRA** inserts small trainable rank-decomposition matrices into frozen model layers.
You update < 1% of parameters instead of all 1.1 billion — training in minutes, not days.

**QLoRA** adds 4-bit quantization so the base model fits in ~6 GB VRAM instead of ~24 GB,
making fine-tuning viable on a single consumer GPU.

**This project fine-tuned on two corpora:**
- 📄 **Legal** — contract clause analysis, regulatory summarization
- 📣 **Marketing** — ad copy generation, tone-matched writing
    """)

    st.markdown("#### LoRA Config Used")
    st.code("""LoraConfig(
    r=64,           # rank — higher = more capacity
    lora_alpha=16,  # scaling factor
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    task_type="CAUSAL_LM"
)
# Result: 0.8% trainable params out of 1.1B total""", language="python")

with col2:
    st.markdown("#### Live Inference — Base Model")
    st.caption("The base TinyLlama-1.1B runs below. Fine-tuned adapters produce more domain-consistent output on legal/marketing prompts.")

    domain = st.selectbox("Preset domain", ["Legal", "Marketing", "General"])
    presets = {
        "Legal":     "Summarize the key obligations a vendor must meet in a standard SaaS MSA agreement.",
        "Marketing": "Write a punchy one-line tagline for a B2B SaaS project management tool targeting ops teams.",
        "General":   "Explain what a large language model is in two clear sentences.",
    }
    prompt = st.text_area("Prompt", value=presets[domain], height=120)

    if st.button("Run Inference", type="primary", use_container_width=True):
        with st.spinner("Calling TinyLlama-1.1B via HuggingFace Inference API…"):
            try:
                result = run_inference(prompt, token)
                st.markdown("**Base model response:**")
                st.info(result)
                st.caption("Fine-tuned adapters (LoRA weights) shift the output style toward legal/marketing conventions.")
            except Exception as e:
                st.error(f"Inference error: {e}")

with st.expander("View Training Script"):
    st.code("""from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments

model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
    load_in_4bit=True,   # QLoRA: 4-bit base model
    device_map="auto"
)
peft_config = LoraConfig(
    r=64, lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1, bias="none", task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
# trainable params: 8,519,680 || all params: 1,109,651,456 || trainable%: 0.77""", language="python")
