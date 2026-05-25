# train_lora_tinyllama.py
import os, math, tempfile
from typing import List, Dict
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    DataCollatorForLanguageModeling, TrainingArguments, Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
from prompt_templates import format_prompt

MODEL_ID   = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs/tinyllama-lora")
SEED       = int(os.environ.get("SEED", 42))
MAX_LENGTH = int(os.environ.get("MAX_LENGTH", 512))
EPOCHS     = float(os.environ.get("EPOCHS", 1))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 1))
GRAD_ACC   = int(os.environ.get("GRAD_ACC", 4))
LR         = float(os.environ.get("LR", 2e-4))

if torch.cuda.is_available():
    DEVICE = "cuda"
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

# Tiny style dataset (same as before)
TRAIN: List[Dict] = [
    {"instruction":"Write an API doc page.",
     "input":"Endpoint: POST /v1/invoices; Auth: Bearer token; Params: customer_id (string, required), line_items (array, required); Response: 201 {invoice_id}",
     "output":"""Summary
Create an invoice for a given customer.

Endpoint
POST /v1/invoices
Auth: Bearer <token>

Parameters
| Name        | Type   | Required | Description                  |
|-------------|--------|----------|------------------------------|
| customer_id | string | yes      | Customer identifier          |
| line_items  | array  | yes      | Line items to be invoiced    |

Responses
- 201 Created: {"invoice_id": "inv_123"}
- 400 Bad Request
- 401 Unauthorized"""
    },
    {"instruction":"Write an API doc page.",
     "input":"Endpoint: GET /v1/invoices/{id}; Auth: Bearer token; Params: id (string, path, required); Response: 200 {invoice}",
     "output":"""Summary
Retrieve an invoice by ID.

Endpoint
GET /v1/invoices/{id}
Auth: Bearer <token>

Parameters
| Name | Type   | Required | In   | Description     |
|------|--------|----------|------|-----------------|
| id   | string | yes      | path | Invoice ID      |

Responses
- 200 OK: {"id":"inv_123","status":"paid",...}
- 401 Unauthorized
- 404 Not Found"""
    },
    {"instruction":"Write an API doc page.",
     "input":"Endpoint: DELETE /v1/invoices/{id}; Auth: Bearer token; Params: id (string, path, required); Response: 204 No Content",
     "output":"""Summary
Delete an invoice by ID.

Endpoint
DELETE /v1/invoices/{id}
Auth: Bearer <token>

Parameters
| Name | Type   | Required | In   | Description     |
|------|--------|----------|------|-----------------|
| id   | string | yes      | path | Invoice ID      |

Responses
- 204 No Content
- 401 Unauthorized
- 404 Not Found"""
    },
    {"instruction":"Write an API doc page.",
     "input":"Endpoint: POST /v1/customers; Auth: Bearer token; Params: email (string, required), name (string, optional); Response: 201 {customer}",
     "output":"""Summary
Create a customer.

Endpoint
POST /v1/customers
Auth: Bearer <token>

Parameters
| Name | Type   | Required | Description        |
|------|--------|----------|--------------------|
| email| string | yes      | Customer email     |
| name | string | no       | Customer name      |

Responses
- 201 Created: {"id":"cus_123", ...}
- 400 Bad Request
- 401 Unauthorized"""
    },
    {"instruction":"Write an API doc page.",
     "input":"Endpoint: PATCH /v1/customers/{id}; Auth: Bearer token; Params: id (string, path, required), name (string, optional); Response: 200 {customer}",
     "output":"""Summary
Update a customer.

Endpoint
PATCH /v1/customers/{id}
Auth: Bearer <token>

Parameters
| Name | Type   | Required | In   | Description    |
|------|--------|----------|------|----------------|
| id   | string | yes      | path | Customer ID    |
| name | string | no       | body | Customer name  |

Responses
- 200 OK: {"id":"cus_123","name":"..."}
- 401 Unauthorized
- 404 Not Found"""
    },
    {"instruction":"Write an API doc page.",
     "input":"Endpoint: GET /v1/customers; Auth: Bearer token; Params: limit (integer, optional), cursor (string, optional); Response: 200 {customers[]}",
     "output":"""Summary
List customers with pagination.

Endpoint
GET /v1/customers
Auth: Bearer <token>

Parameters
| Name   | Type    | Required | Description                 |
|--------|---------|----------|-----------------------------|
| limit  | integer | no       | Max items to return         |
| cursor | string  | no       | Pagination cursor           |

Responses
- 200 OK: [{"id":"cus_..."}...]
- 401 Unauthorized"""
    },
]

def row_to_text(r: Dict) -> str:
    return format_prompt(r["instruction"], r["input"]) + r["output"]

def main():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"

    ds_train = Dataset.from_list(TRAIN)
    ds_eval  = Dataset.from_list(TRAIN[:2])

    cols = list(ds_train.features.keys())
    tok_train = ds_train.map(lambda ex: tok(row_to_text(ex), truncation=True, max_length=MAX_LENGTH, padding=False), remove_columns=cols)
    tok_eval  = ds_eval.map (lambda ex: tok(row_to_text(ex), truncation=True, max_length=MAX_LENGTH, padding=False), remove_columns=cols)

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
        # Older transformers may not support report_to; include only if present:
        # report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tok_train,
        eval_dataset=tok_eval,
        data_collator=collator,
        tokenizer=tok,
    )

    print("\n=== Training LoRA adapter (tiny run) ===")
    trainer.train()

    # Save adapter weights
    adapter_dir = os.path.join(OUTPUT_DIR, "adapter")
    os.makedirs(adapter_dir, exist_ok=True)
    trainer.model.save_pretrained(adapter_dir)
    tok.save_pretrained(OUTPUT_DIR)

    # Tiny eval
    try:
        metrics = trainer.evaluate(tok_eval)
        if "eval_loss" in metrics:
            import math
            print(f"Eval loss: {metrics['eval_loss']:.4f} | ppl≈{math.exp(float(metrics['eval_loss'])):.2f}")
    except Exception as e:
        print("Eval skipped:", repr(e))

    print(f"\nSaved LoRA adapter to: {adapter_dir}")

if __name__ == "__main__":
    main()
