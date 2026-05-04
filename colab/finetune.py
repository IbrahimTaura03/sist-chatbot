import torch
import os
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
DATA_PATH  = "../data/sist_qa.json"
OUTPUT_DIR = "../sist-adapter"

print("Step 1/5: Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

print("Step 2/5: Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    low_cpu_mem_usage=True,
    torch_dtype=torch.float32,
)

print("Step 3/5: Applying LoRA adapter...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("Step 4/5: Loading and formatting dataset...")
dataset = load_dataset("json", data_files=DATA_PATH, split="train")

def format_example(example):
    return {
        "text": f"[INST] {example['question']} [/INST] {example['answer']}"
    }

dataset = dataset.map(format_example)
print(f"  Loaded {len(dataset)} training examples")

print("Step 5/5: Starting training...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    warmup_steps=5,
    learning_rate=2e-4,
    fp16=False,
    logging_steps=5,
    save_steps=100,
    save_total_limit=2,
    optim="adamw_torch",
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
    args=training_args,
)

trainer.train()

print("Saving adapter...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"✅ Adapter saved to {OUTPUT_DIR}")
for f in os.listdir(OUTPUT_DIR):
    print(f"  - {f}")
