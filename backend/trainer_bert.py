import pandas as pd
import torch
import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

# 1. APRENDIZAJE
print("--- INICIANDO APRENDIZAJE (BERT-TINY) ---")
raw_datasets = load_dataset("dair-ai/emotion")

# Limitamos a 2000 para que no tarde una eternidad en la demo
N_LINEAS = 2000 
raw_datasets["train"] = raw_datasets["train"].select(range(N_LINEAS))

model_name = "prajjwal1/bert-tiny"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_fn(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=64)

tokenized_datasets = raw_datasets.map(tokenize_fn, batched=True)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=6)

# 2. ENTRENAMIENTO RÁPIDO
args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    use_cpu=True,
    report_to="none"
)

trainer = Trainer(model=model, args=args, train_dataset=tokenized_datasets["train"])
trainer.train()

# 3. FUNCIÓN QUE USA EL ANALYZER
id2label = {0: "sadness", 1: "joy", 2: "love", 3: "anger", 4: "fear", 5: "surprise"}

def get_sentiment_profile(text):
    if not text or pd.isna(text):
        return {emo: 0.0 for emo in ["joy", "sadness", "fear", "surprise", "anger", "disgust", "average_sentiment"]}
    
    inputs = tokenizer(str(text)[:512], return_tensors="pt", padding=True, truncation=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    
    p = {id2label[i]: float(probs[i]) for i in range(len(id2label))}
    
    # Mapeo final
    profile = {
        "joy": p.get("joy", 0) + p.get("love", 0),
        "sadness": p.get("sadness", 0),
        "fear": p.get("fear", 0),
        "surprise": p.get("surprise", 0),
        "anger": p.get("anger", 0),
        "disgust": 0.0
    }
    profile["average_sentiment"] = (profile["joy"] + profile["surprise"]) / (sum(profile.values()) + 1e-9)
    return profile