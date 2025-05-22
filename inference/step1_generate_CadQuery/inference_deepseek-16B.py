from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForCausalLM
from peft import PeftModel
import torch
import os
import json
from tqdm import tqdm

test_dataset = './test_filtered.jsonl'
base_model_id = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
output_dir = './txt_deepseek'

tokenizer = AutoTokenizer.from_pretrained(
    base_model_id,
    trust_remote_code=True,
    use_fast=False,
    model_max_length=1024
)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

base_model = AutoModelForCausalLM.from_pretrained(base_model_id, trust_remote_code=True)
model = PeftModel.from_pretrained(base_model, "/home/tc415/CAD4Protein/Text-to-CadQuery/train/lora_deepseek16b_best").to("cuda")
model.eval()

batch_size = 5

with open(test_dataset, 'r') as f_in:
    lines = [json.loads(line) for line in f_in][:batch_size*4]

for i in range(0, len(lines), batch_size):
    batch = lines[i:i+batch_size]
    prompts = [
    f"<s>[INST] {ex['input']} [/INST]"
    for ex in batch
    ]

    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to("cuda")

    input_lengths = inputs["input_ids"].shape[1]
    max_new_tokens = max(1, 1024 - input_lengths)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False
        )

    decoded_outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    for j, output in enumerate(decoded_outputs):
        if "[/INST]" in output:
            response = output.split("[/INST]", 1)[1].strip()
        else:
            response = output
        with open(os.path.join(output_dir, f"{i + j}.txt"), "w") as f_out:
            f_out.write(response.strip())
    