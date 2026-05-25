import os, math
from typing import List, Dict
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    DataCollatorForLanguageModeling, TrainingArguments, Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
from prompt_template_marketing import format_prompt_marketing

MODEL_ID    = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
OUTPUT_DIR  = os.environ.get("OUTPUT_DIR", "outputs/tinyllama-marketing-lora")
SEED        = int(os.environ.get("SEED", 42))
MAX_LENGTH  = int(os.environ.get("MAX_LENGTH", 512))
EPOCHS      = float(os.environ.get("EPOCHS", 1))
BATCH_SIZE  = int(os.environ.get("BATCH_SIZE", 1))
GRAD_ACC    = int(os.environ.get("GRAD_ACC", 4))
LR          = float(os.environ.get("LR", 2e-4))

if torch.cuda.is_available():
    DEVICE = "cuda"
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

# --- Tiny MARKETING dataset (short, punchy, varied surfaces) ---
MKT_TRAIN: List[Dict] = [
    {
        "instruction": "Write a witty Instagram caption for a new eco-friendly water bottle.",
        "input": "Brand: AquaLeaf; USP: keeps water cold 24h; Audience: college students; Tone: playful",
        "output": "Stay cool for 24 hours straight—unlike your group project. 💧 #AquaLeaf #EcoFriendly"
    },
    {
        "instruction": "Draft a persuasive headline and subhead for a display ad.",
        "input": "Product: Project management SaaS; Benefit: save 10 hrs/week; Tone: confident",
        "output": "Own Your Week.\nStop juggling. Start delivering—save up to 10 hours every week."
    },
    {
        "instruction": "Write 5 email subject lines that feel personal yet professional.",
        "input": "Product: TypoZero AI writing assistant; CTA: Try free today",
        "output": "1) Your draft, but sharper ✍️\n2) 5 minutes to a polished pitch\n3) TypoZero can save your morning\n4) Hit send with confidence\n5) Write less. Win more."
    },
    {
        "instruction": "Write a short product description with a strong CTA.",
        "input": "Brand: ZenX; Product: smartphone; USP: 3-day battery life; Audience: busy professionals",
        "output": "Meet ZenX—the phone that outlasts your calendar. Power through 3 days on a single charge. Switch now and stop hunting for outlets."
    },
    {
        "instruction": "Give 5 tagline options for a green energy startup.",
        "input": "Brand: VerdantGrid; Promise: cleaner power, lower bills",
        "output": "1) Power the change.\n2) Clean energy, real savings.\n3) Your bill, reimagined.\n4) Greener grid. Brighter homes.\n5) Switch on a better future."
    },
    {
        "instruction": "Write a LinkedIn post announcing a product launch.",
        "input": "Product: DataViz Pro 2.0; Features: one-click dashboards, Slack alerts; CTA: Book a demo",
        "output": "We built DataViz Pro 2.0 to make insights impossible to miss. One-click dashboards + Slack alerts = decisions at the speed of chat. Book a demo and see your data tell clearer stories."
    },
    {
        "instruction": "Create 3 Google ad variants (30-char headline + 90-char desc).",
        "input": "Product: FlowNote note-taking app; Hook: organize your day fast; CTA: Start free",
        "output": "H: Organize Your Day Fast\nD: Capture ideas, plan tasks, and focus in minutes. Start free.\n\nH: Write Less, Remember More\nD: Smart notes that surface when you need them. Try FlowNote.\n\nH: Notes that Work for You\nD: Tag, search, and sync everywhere—without the clutter."
    },
    {
        "instruction": "Draft a short landing page hero copy.",
        "input": "Product: PixLift background remover; Audience: marketers; Proof: used by 5k+ brands",
        "output": "Design-ready images in seconds.\nRemove backgrounds with pixel-perfect precision—trusted by 5,000+ brands.\nGet started free."
    },
]

MKT_EVAL = MKT_TRAIN[:2]

def row_to_text(r: Dict) -> str:
    return format_prompt_marketing(r["instruction"], r["input"]) + r["output"]

def main():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"

    ds_train = Dataset.from_list(MKT_TRAIN)
    ds_eval  = Dataset.from_list(MKT_EVAL)

    cols = list(ds_train.features.keys())
    tok_train = ds_train.map(lambda ex: tok(row_to_text(ex), truncation=True, max_length=MAX_LENGTH, padding=False),
                             remove_columns=cols)
    tok_eval  = ds_eval.map (lambda ex: tok(row_to_text(ex), truncation=True, max_length=MAX_LENGTH, padding=False),
                             remove_columns=cols)

    base = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    if hasattr(base, "gradient_checkpointing_enable"):
        try:
            base.gradient_checkpointing_enable()
            base.config.use_cache = False
        except Exception:
            pass
    base.to(DEVICE)

    lora_cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8, lora_alpha=16, lora_dropout=0.05,
        target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]
    )
    model = get_peft_model(base, lora_cfg)

    collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        seed=SEED,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACC,
        learning_rate=LR,
        logging_steps=5,
        save_steps=1000,
        dataloader_pin_memory=False,
        # keep minimal args for older transformers
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tok_train,
        eval_dataset=tok_eval,
        data_collator=collator,
        tokenizer=tok,
    )

    print("\n=== Training MARKETING LoRA adapter (tiny run) ===")
    trainer.train()

    # Save adapter
    adapter_dir = os.path.join(OUTPUT_DIR, "adapter")
    os.makedirs(adapter_dir, exist_ok=True)
    trainer.model.save_pretrained(adapter_dir)
    tok.save_pretrained(OUTPUT_DIR)

    # Quick eval (loss → perplexity)
    try:
        metrics = trainer.evaluate(tok_eval)
        if "eval_loss" in metrics:
            print(f"Eval loss: {metrics['eval_loss']:.4f} | ppl≈{math.exp(float(metrics['eval_loss'])):.2f}")
    except Exception as e:
        print("Eval skipped:", repr(e))

    print(f"\nSaved MARKETING LoRA adapter to: {adapter_dir}")

if __name__ == "__main__":
    main()
