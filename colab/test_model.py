import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL_NAME  = "mistralai/Mistral-7B-Instruct-v0.2"
ADAPTER_DIR = "../sist-adapter"

print("Loading model for testing...")
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float32,
)
model     = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR)
print("✅ Model loaded")

def ask(question: str) -> str:
    prompt = f"[INST] {question} [/INST]"
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
        )
    full = tokenizer.decode(output[0], skip_special_tokens=True)
    return full.split("[/INST]")[-1].strip()

test_questions = [
    "What programmes does SIST Tangier offer?",
    "How do I apply to SIST?",
    "What is the Foundation Year?",
    "Does SIST offer scholarships?",
    "Where is SIST Tangier located?",
    "What English level is required to join SIST?",
    "Can I transfer to a UK university from SIST?",
    "What degrees do SIST students receive?",
    "When is the next intake at SIST?",
    "Is SIST accredited?",
]

print("\n" + "="*60)
print("MODEL EVALUATION — SIST Chatbot")
print("="*60)

for i, q in enumerate(test_questions, 1):
    answer = ask(q)
    print(f"\nQ{i}: {q}")
    print(f"A:  {answer}")
    print("-"*40)
