from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import load_dataset, load_from_disk
from peft import get_peft_model, LoraConfig, TaskType
from transformers import DataCollatorForLanguageModeling
import torch

model_path = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
# model_path = "deepseek-ai/deepseek-llm-7b-base"

tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    trust_remote_code=True,
    use_fast=False,
    model_max_length=1024
)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

# train_raw = load_dataset("json", data_files="/home/tc415/CAD4Protein/Text-to-CadQuery/dataset/data/data_train.jsonl", split="train")
# val_raw = load_dataset("json", data_files="/home/tc415/CAD4Protein/Text-to-CadQuery/dataset/data/data_val.jsonl", split="train")

# def format_mistral_prompt(example):
#     prompt = f"<s>[INST] {example['input']} [/INST] {example['output']}</s>"
#     return prompt

# def count_length(example):
#     prompt = format_mistral_prompt(example)
#     tokens = tokenizer(prompt, truncation=False)
#     example["length"] = len(tokens["input_ids"])
#     return example

# train_with_length = train_raw.map(count_length)
# val_with_length = val_raw.map(count_length)
# train_filtered = train_with_length.filter(lambda x: x["length"] <= 1024)
# val_filtered = val_with_length.filter(lambda x: x["length"] <= 1024)

# def preprocess(example):
#     prompt = format_mistral_prompt(example)
#     return tokenizer(prompt, truncation=True, padding="max_length", max_length=1024)

# train_dataset = train_filtered.map(preprocess, remove_columns=train_filtered.column_names)
# val_dataset = val_filtered.map(preprocess, remove_columns=val_filtered.column_names)

# train_dataset.save_to_disk('/home/tc415/CAD4Protein/Text-to-CadQuery/dataset/processed/train')
# val_dataset.save_to_disk('/home/tc415/CAD4Protein/Text-to-CadQuery/dataset/processed/val')
# print("Saved to disk!")
train_dataset = load_from_disk("/home/tc415/CAD4Protein/Text-to-CadQuery/dataset/processed/train")
val_dataset   = load_from_disk("/home/tc415/CAD4Protein/Text-to-CadQuery/dataset/processed/val")

from transformers import BitsAndBytesConfig
from peft import prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    trust_remote_code=True,
    device_map="auto"
)

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    # use_dora=True
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

training_args = TrainingArguments(
    output_dir="./checkpoints_deepseek16b_lora",
    # per_device_train_batch_size=64,
    # per_device_eval_batch_size=32,
    # gradient_accumulation_steps=1,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=16,
    gradient_accumulation_steps=2,
    num_train_epochs=4,
    learning_rate=5e-5,
    bf16=True,d
    
    # ────────────────────────────────────────────────────────────────────
    # 1. Evaluate every N steps (match your logging_steps)
    evaluation_strategy="steps",
    eval_steps=50,

    # 2. Save a checkpoint every N steps
    save_strategy="steps",
    save_steps=50,

    # 3. Only keep the best model (lowest eval loss)
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    save_total_limit=1,
    # ────────────────────────────────────────────────────────────────────

    logging_steps=50,
    logging_dir="./logs_deepseek16b_lora",
    # save_strategy="epoch",
    # save_total_limit=2,
    report_to="none",
    dataloader_num_workers=4,
    dataloader_prefetch_factor=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

trainer.train()

# model.save_pretrained("./lora_deepseek16b_adapter")
trainer.save_model("./lora_deepseek16b_best")

