import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class CodeCompletionDataset:
    """
    This class implements the tokenization of the dataset representing code completion input and output samples.
    """

    def __init__(self, dataset, tokenizer, max_length=8, verbose=False):
        self.dataset = dataset
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.verbose = verbose

    def __len__(self):
        return len(self.context_list)

    def tokenize_item(self, context, groundtruth):
        # Tokenize context and groundtruth
        input_encoding = self.tokenizer(
            context,
            padding="max_length",
            truncation=True,
            max_length=256,
            return_tensors="pt",
        )

        target_encoding = self.tokenizer(
            groundtruth,
            padding="max_length",
            truncation=True,
            max_length=256,
            return_tensors="pt",
        )

        # Flatten the tensors to be compatible with the model
        input_ids = input_encoding["input_ids"]
        attention_mask = input_encoding["attention_mask"]
        labels = target_encoding["input_ids"]

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    def tokenize_dataset(self):
        tokenized_dataset = []

        # Initialize statistics
        context_lengths = 0
        groundtruth_lengths = 0
        min_max_context = {"min": float("inf"), "max": -float("inf")}
        min_max_groundtruth = {"min": float("inf"), "max": -float("inf")}

        for entry in self.dataset:
            context = entry["context"]
            groundtruth = entry["groundtruth"]
            context_length = entry["context_length"]
            groundtruth_length = entry["groundtruth_length"]

            tokenized_entry = self.tokenize_item(context, groundtruth)
            tokenized_dataset.append(tokenized_entry)

            context_lengths += context_length
            groundtruth_lengths += groundtruth_length

            # Update min/max using defaults
            min_max_context["min"] = min(min_max_context["min"], context_length)
            min_max_context["max"] = max(min_max_context["max"], context_length)

            min_max_groundtruth["min"] = min(
                min_max_groundtruth["min"], groundtruth_length
            )
            min_max_groundtruth["max"] = max(
                min_max_groundtruth["max"], groundtruth_length
            )

        # Calculate averages
        avg_context_length = context_lengths / len(self.dataset)
        avg_groundtruth_length = groundtruth_lengths / len(self.dataset)

        # Output statistics
        if self.verbose:
            logger.info(f"Average context length: {avg_context_length}")
            logger.info(f"Average groundtruth length: {avg_groundtruth_length}")
            logger.info(f"Min context length: {min_max_context['min']}")
            logger.info(f"Max context length: {min_max_context['max']}")
            logger.info(f"Min groundtruth length: {min_max_groundtruth['min']}")
            logger.info(f"Max groundtruth length: {min_max_groundtruth['max']}")

        return tokenized_dataset
