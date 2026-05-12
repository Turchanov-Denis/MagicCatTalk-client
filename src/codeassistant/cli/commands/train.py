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


def train(config):

    # =========================
    # CUDA CHECK
    # =========================
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    print("GPU:", torch.cuda.get_device_name(0))

    # =========================
    # CONFIG VALIDATION
    # =========================
    required = [
        "model",
        "dataset",
        "input_col",
        "output_col",
        "output_dir"
    ]

    for key in required:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    # =========================
    # MODEL
    # =========================
    model_name = config["model"].replace("\\", "/").strip()

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )

    if tokenizer.pad_token is None:
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
    dataset_name = config["dataset"]

    if not isinstance(dataset_name, str):
        raise ValueError("config['dataset'] must be a string")

    ds = load_dataset(dataset_name)

    dataset = ds["train"] if "train" in ds else ds

    # =========================
    # COLUMN VALIDATION
    # =========================
    columns = dataset.column_names

    if config["input_col"] not in columns:
        raise ValueError(f"Input column not found: {config['input_col']}")

    if config["output_col"] not in columns:
        raise ValueError(f"Output column not found: {config['output_col']}")

    context_col = config.get("context_col")

    if context_col and context_col not in columns:
        raise ValueError(f"Context column not found: {context_col}")

    # =========================
    # FILTER
    # =========================
    dataset = dataset.filter(
        lambda x: (
            not x.get("is_negative", False)
            and len(str(x.get(config["input_col"], ""))) > 50
            and len(str(x.get(config["output_col"], ""))) > 20
        )
    )

    # =========================
    # SYSTEM PROMPT
    # =========================
    system_prompt = config.get("system_prompt", "")

    # =========================
    # FORMATTER
    # =========================
    def format_example(example):

        input_text = str(example.get(config["input_col"], ""))
        output_text = str(example.get(config["output_col"], ""))

        context_text = ""

        if context_col:
            context_text = str(example.get(context_col, ""))

        response_prefix = ""

        if context_text:
            response_prefix = f"Type: {context_text}\n"

        return {
            "text": f"""### Instruction:
{system_prompt}

### Input:
{input_text}

### Response:
{response_prefix}{output_text}"""
        }

    dataset = dataset.map(
        format_example,
        remove_columns=dataset.column_names
    )

    # =========================
    # LIMIT DATASET
    # =========================
    dataset_size = config.get("dataset_size")

    if dataset_size:
        dataset = dataset.select(
            range(min(dataset_size, len(dataset)))
        )

    print("Train size:", len(dataset))
    print(dataset[0])

    # =========================
    # TRAINING
    # =========================
    training_cfg = config.get("training", {})

    training_args = TrainingArguments(
        output_dir=config["output_dir"],
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        max_steps=training_cfg.get("max_steps", 100),
        logging_steps=10,
        fp16=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
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
    model.save_pretrained(config["output_dir"])
    tokenizer.save_pretrained(config["output_dir"])

    print("✅ Training finished")