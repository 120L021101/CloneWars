import argparse
import logging

import torch
from datasets import load_dataset
from transformers import AutoTokenizer
from joblib import dump

from llm_evaluation.code_completion_tokenizer import CodeCompletionDataset
from llm_evaluation.eval_pipeline import EvalPipeline
from llm_evaluation.pre_processing import PreProcessing

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    # Logging for debugging purposes on DelftBlue
    logger.info(f"Cuda's version: {torch.version.cuda}")
    logger.info(f"Is Cuda available: {torch.cuda.is_available()}")

    parser = argparse.ArgumentParser(
        description="Evaluate the CodeParrot model on code completion tasks."
    )

    parser.add_argument(
        "--model",
        "-m",
        type=str,
        required=False,
        default="codeparrot/codeparrot",
        help="The model to evaluate on code completion task (CodeParrot default).",
    )

    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        required=False,
        default="nada-mou/ML4SE-exact-dedup-file-final",
        help="The dataset to evaluate the model on.",
    )

    parser.add_argument(
        "--num-samples",
        "-n",
        type=int,
        required=False,
        default=None,
        help="The number of samples to evaluate the model on.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        required=False,
        help="Increase output verbosity.",
    )

    # Parse the arguments
    args = parser.parse_args()
    model_name = args.model
    dataset_name = args.dataset
    num_samples = args.num_samples

    # Input Validation
    if not model_name:
        raise ValueError(
            "Please specify the model to evaluate on code completion tasks."
        )
    if not dataset_name:
        raise ValueError("Please specify the dataset to evaluate the model on.")
    if num_samples is not None and num_samples < 3:
        raise ValueError(
            "Please specify a valid number of samples to evaluate the model on."
        )

    logger.info(
        f"Evaluating model: '{model_name}' on dataset: '{dataset_name}' for {num_samples if num_samples else 'all'} samples."
    )

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # Load the dataset
    logger.info(f"Loading dataset: {dataset_name}")
    complete_dataset = load_dataset(dataset_name, split="train")
    logger.info(f"Total number of samples in the dataset: {len(complete_dataset)}")

    # Sample the dataset if required
    eval_dataset = (
        complete_dataset if num_samples is None else complete_dataset[:num_samples]
    )

    # Preprocess the dataset for code completion
    logger.info("Preprocessing the dataset...")
    preprocessing = PreProcessing(
        dataset=eval_dataset, model=model_name, verbose=args.verbose
    )
    dataset = preprocessing.preprocess_dataset()

    # Backup the preprocessed dataset
    dump(dataset, f'preprocessed_dataset_{dataset_name.replace("/", "")}.joblib')

    # Tokenize the datasets into inputs and labels
    logger.info("Tokenizing the dataset...")
    dataset_tokenizer = CodeCompletionDataset(dataset, tokenizer, verbose=args.verbose)
    tokenized_dataset = dataset_tokenizer.tokenize_dataset()

    # Backup the tokenized dataset
    dump(tokenized_dataset, f'tokenized_dataset_{dataset_name.replace("/", "")}.joblib')

    # Evaluate the model on code completion
    logger.info("Evaluating the model on code completion tasks...")
    eval_pipeline = EvalPipeline(tokenized_dataset, tokenizer, model_name)
    eval_pipeline.model_evaluate()
