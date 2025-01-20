from transformers import (
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

"""
This module represents the finetuning implementation for CodeParrot on code completion.
However, it was eventually not used in our paper, so it can be disregarded.
"""


class FineTunePipeline:
    def __init__(
        self, tokenized_dataset, tokenizer, model_name="codeparrot/codeparrot"
    ):
        self.tokenizer = tokenizer
        self.tokenized_dataset = tokenized_dataset
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.training_args = TrainingArguments(
            output_dir="test_trainer",
            eval_strategy="epoch",
            learning_rate=5e-2,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=5,
            weight_decay=0.01,
            prediction_loss_only=True,
            include_for_metrics=["inputs", "loss"],
        )

    def model_training(self, train_size=0.8):
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )
        self.model.config.pad_token_id = self.model.config.eos_token_id
        split_idx = int(len(self.tokenized_dataset) * train_size)

        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=self.tokenized_dataset[:split_idx],
            eval_dataset=self.tokenized_dataset[split_idx:],
            data_collator=data_collator,
        )

        trainer.train()

        # Evaluate perplexity on the validation set after training is complete
        self.evaluate_perplexity(trainer)

    def evaluate_perplexity(self, trainer):
        pass
