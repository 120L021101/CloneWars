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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def main():
    # Log CUDA information
    logger.info(f"CUDA version: {torch.version.cuda}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")

    # Argument parsing
    parser = argparse.ArgumentParser(description="Evaluate CodeParrot model on code completion tasks.")
    parser.add_argument("-m", "--model", type=str, default="codeparrot/codeparrot",
                        help="Model for code completion evaluation (default: CodeParrot).")
    parser.add_argument("-d", "--dataset", type=str, default="nada-mou/ML4SE-exact-dedup-file-final",
                        help="Dataset to evaluate the model on.")
    parser.add_argument("-n", "--num-samples", type=int, default=None,
                        help="Number of samples to evaluate (default: all).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity.")

    args = parser.parse_args()

    # Input validation
    if args.num_samples is not None and args.num_samples < 3:
        raise ValueError("Number of samples must be at least 3 or None for full dataset.")

    logger.info(f"Evaluating model '{args.model}' on dataset '{args.dataset}' for {args.num_samples or 'all'} samples.")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    tokenizer.pad_token = tokenizer.eos_token

    # Load dataset
    logger.info(f"Loading dataset: {args.dataset}")
    complete_dataset = load_dataset(args.dataset, split="train")
    logger.info(f"Total samples in dataset: {len(complete_dataset)}")

    # Sample dataset if required
    eval_dataset = complete_dataset if args.num_samples is None else complete_dataset.select(range(args.num_samples))

    # Preprocess dataset
    logger.info("Preprocessing dataset...")
    dataset = PreProcessing(eval_dataset, args.model, args.verbose).preprocess_dataset()

    # Backup preprocessed dataset
    dump(dataset, f'preprocessed_{args.dataset.replace("/", "_")}.joblib')

    # Tokenize dataset
    logger.info("Tokenizing dataset...")
    tokenized_dataset = CodeCompletionDataset(dataset, tokenizer, args.verbose).tokenize_dataset()

    # Backup tokenized dataset
    dump(tokenized_dataset, f'tokenized_{args.dataset.replace("/", "_")}.joblib')

    # Evaluate model
    logger.info("Evaluating model on code completion tasks...")
    EvalPipeline(tokenized_dataset, tokenizer, args.model).model_evaluate()

if __name__ == "__main__":
    main()
