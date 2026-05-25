import os, math
from typing import List, Dict
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    DataCollatorForLanguageModeling, TrainingArguments, Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
from prompt_templates import format_prompt_legal

MODEL_ID    = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
OUTPUT_DIR  = os.environ.get("OUTPUT_DIR", "outputs/tinyllama-legal-lora")
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

# ---- Tiny LEGAL dataset (style & content patterns) ----
# Keep outputs short and consistent. Each sample shows one clause or a short section set.
LEGAL_TRAIN: List[Dict] = [
    {
        "instruction": "Draft a Confidentiality clause.",
        "input": "Parties: Alpha Corp and Beta LLC; Duration: 3 years; Standard carve-outs apply.",
        "output": """Confidentiality
Each Party shall keep the other Party’s Confidential Information strictly confidential and not disclose it to any third party, except to Affiliates, employees, and advisors who have a need to know and are bound by obligations no less protective than this Section. Confidentiality obligations survive for 3 years after termination. Confidential Information does not include information that is publicly available, already known without duty of confidentiality, independently developed, or rightfully received from a third party without restriction."""
    },
    {
        "instruction": "Draft a Termination for Convenience clause.",
        "input": "Notice: 30 days; Fees owed remain payable.",
        "output": """Termination for Convenience
Either Party may terminate this Agreement for convenience upon thirty (30) days’ prior written notice. Termination does not relieve either Party of any payment obligations accrued before the effective date of termination."""
    },
    {
        "instruction": "Draft a Limitation of Liability clause.",
        "input": "Cap: fees paid in prior 12 months; Exclude indirect damages; Carve-out: breach of confidentiality, IP infringement.",
        "output": """Limitation of Liability
Except for liability arising from breach of Confidentiality or infringement of intellectual property rights, in no event will either Party be liable for any indirect, incidental, special, consequential, or punitive damages. Each Party’s aggregate liability under this Agreement will not exceed the fees paid or payable in the twelve (12) months preceding the event giving rise to the claim."""
    },
    {
        "instruction": "Draft an Indemnification clause.",
        "input": "Scope: third-party IP claims; Remedy: defend, indemnify, hold harmless; Exclusions: misuse, modification.",
        "output": """Indemnification
Provider will defend, indemnify, and hold Customer harmless from any third-party claim alleging that the Services infringe such third party’s intellectual property rights, and pay damages and reasonable costs finally awarded. Provider has no obligation for claims arising from Customer’s misuse, combination with non-Provider products, or modifications not authorized by Provider."""
    },
    {
        "instruction": "Draft a Governing Law and Venue clause.",
        "input": "Jurisdiction: State of Delaware; Venue: federal and state courts in New Castle County.",
        "output": """Governing Law; Venue
This Agreement is governed by the laws of the State of Delaware, without regard to conflicts of laws rules. The Parties consent to the exclusive jurisdiction and venue of the state and federal courts located in New Castle County, Delaware."""
    },
    {
        "instruction": "Draft a Data Protection clause.",
        "input": "Standard: GDPR-compliant; Subprocessors allowed with notice; Security: industry-standard measures.",
        "output": """Data Protection
Provider will implement and maintain industry-standard administrative, physical, and technical safeguards appropriate to the nature of the data processed. Provider may use Subprocessors subject to written agreements imposing data protection obligations no less protective than those herein and will notify Customer of material Subprocessor changes. Where applicable, the Parties will execute a data processing agreement to address GDPR requirements."""
    },
    {
        "instruction": "Draft a Force Majeure clause.",
        "input": "Events: natural disasters, war, labor disputes, failures of utilities; Duty to mitigate; Notice required.",
        "output": """Force Majeure
Neither Party is liable for delay or failure to perform due to events beyond its reasonable control, including acts of God, war, terrorism, labor disputes, or failures of utilities or communications. The affected Party will provide prompt notice and use commercially reasonable efforts to mitigate the impact. Performance is excused only for the duration of the event."""
    },
    {
        "instruction": "Draft a Notices clause.",
        "input": "Method: email + registered mail; Effective upon receipt; Include addresses.",
        "output": """Notices
All notices must be in writing and delivered by email and registered mail to the addresses specified by the Parties. Notices are effective upon receipt, as evidenced by delivery confirmation."""
    },
]

LEGAL_EVAL = LEGAL_TRAIN[:2]  # tiny eval

def row_to_text(r: Dict) -> str:
    return format_prompt_legal(r["instruction"], r["input"]) + r["output"]

def main():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"

    ds_train = Dataset.from_list(LEGAL_TRAIN)
    ds_eval  = Dataset.from_list(LEGAL_EVAL)

    cols = list(ds_train.features.keys())
    tok_train = ds_train.map(lambda ex: tok(row_to_text(ex), truncation=True, max_length=MAX_LENGTH, padding=False),
                             remove_columns=cols)
    tok_eval  = ds_eval.map (lambda ex: tok(row_to_text(ex), truncation=True, max_length=MAX_LENGTH, padding=False),
                             remove_columns=cols)

    base = AutoModelForCausalLM.from_pretrained(MODEL_ID)
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

    print("\n=== Training LEGAL LoRA adapter (tiny run) ===")
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

    print(f"\nSaved LEGAL LoRA adapter to: {adapter_dir}")

if __name__ == "__main__":
    main()
