import logging
import torch

from transformers import (
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class EvalPipeline:
    """
    This class is used for starting the evaluation pipeline for the provided tokenized dataset.
    """

    def __init__(self, tokenized_dataset, tokenizer, model_name):
        self.tokenizer = tokenizer
        self.tokenized_dataset = tokenized_dataset
        self.model_name = model_name
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.training_args = TrainingArguments(
            output_dir="test_trainer",
            eval_strategy="epoch",
            prediction_loss_only=True,
            include_for_metrics=["inputs", "loss"],
        )

    def model_evaluate(self):
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )
        self.model.config.pad_token_id = self.model.config.eos_token_id

        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=None,
            eval_dataset=self.tokenized_dataset,
            data_collator=data_collator,
        )

        logger.info("Evaluating the model on the tokenized dataset...")
        self.evaluate_perplexity(trainer=trainer)
        logger.info("Evaluation complete!")

    def evaluate_perplexity(self, trainer):
        """
        Evaluate the model perplexity on the provided dataset, as well as log the results.
        :param trainer: The Trainer object used for evaluation (transformers.Trainer)
        :return: None
        """

        eval_results = trainer.evaluate()
        perplexity = torch.exp(torch.tensor(eval_results["eval_loss"]))
        trainer.log_metrics(split="eval", metrics=eval_results)
        logger.info(f"Perplexity of '{self.model_name}': {perplexity.item()}")
