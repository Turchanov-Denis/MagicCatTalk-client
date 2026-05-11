import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

# =========================
# GPU CHECK
# =========================
assert torch.cuda.is_available()
print("GPU:", torch.cuda.get_device_name(0))

# =========================
# MODEL
# =========================
model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# =========================
# LORA
# =========================
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
)

model = get_peft_model(model, lora_config)

# =========================
# DATASET
# =========================
dataset = load_dataset("ronantakizawa/github-codereview")

# -------------------------
# FILTER (очень важно)
# -------------------------
dataset = dataset.filter(
    lambda x: (
        not x["is_negative"] and
        len(x["before_code"]) > 50 and
        len(x["reviewer_comment"]) > 20
    )
)

# -------------------------
# FORMAT
# -------------------------
SYSTEM_PROMPT = """You are a senior software engineer.

Perform strict code review focusing on:
- bugs
- performance issues
- security issues
- bad practices
"""

def format_example(example):
    code = example["before_code"]
    review = example["reviewer_comment"]
    comment_type = example.get("comment_type", "")

    return {
        "text": f"""### Instruction:
{SYSTEM_PROMPT}

### Input:
{code}

### Response:
Type: {comment_type}
{review}"""
    }

dataset = dataset.map(format_example)

# -------------------------
# OPTIONAL: уменьшить dataset для теста
# -------------------------
train_dataset = dataset["train"].select(range(5000))

print("Train size:", len(train_dataset))
print(train_dataset[0])

# =========================
# TRAINING
# =========================
training_args = TrainingArguments(
    output_dir="../../../lora/codereview-lora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    max_steps=500,
    logging_steps=10,
    save_steps=100,
    fp16=True,
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=training_args,
)

# =========================
# TRAIN
# =========================
trainer.train()

# =========================
# SAVE
# =========================
model.save_pretrained("codereview-lora")
tokenizer.save_pretrained("codereview-lora")

print("✅ Training finished")