import torch
from datasets import load_dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)

if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
else:
    print("CUDA is not available. Using CPU.")

# load dataset and tokenizer
dataset = load_dataset("ZujiZhou/ML4SE", cache_dir="/scratch/zujizhou/test")
tokenizer = AutoTokenizer.from_pretrained(
    "HuggingFaceTB/SmolLM-360M", cache_dir="/scratch/zujizhou/model"
)
tokenizer.pad_token = tokenizer.eos_token


# dataset pre-processing
def tokenize_function(example):
    inputs = tokenizer(
        example["content"], truncation=True, padding="max_length", max_length=512
    )
    inputs["labels"] = inputs["input_ids"].copy()
    return inputs


# tokenize the whole dataset
tokenized_dataset = dataset.map(
    tokenize_function, batched=True, remove_columns=["content"]
)

tokenized_dataset.save_to_disk("/scratch/zujizhou/test")

# all the dataset for training
train_dataset = tokenized_dataset

# load model
model = AutoModelForCausalLM.from_pretrained(
    "HuggingFaceTB/SmolLM-360M", cache_dir="/scratch/zujizhou/model"
)

# train params
training_args = TrainingArguments(
    output_dir="/scratch/zujizhou/output",  # model save path
    evaluation_strategy="no",  # do not eval
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    save_steps=10_000,
    save_total_limit=2,
    logging_dir="/scratch/zujizhou/logs",  # log save path
    logging_steps=500,
    fp16=True,
    push_to_hub=False,
)

# define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# start training
trainer.train()

# save model
model.save_pretrained("/scratch/zujizhou/output")
tokenizer.save_pretrained("/scratch/zujizhou/output")
