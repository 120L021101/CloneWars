import gc
import hashlib
from datasets import load_dataset

def compute_hash_256(message):
    return hashlib.sha256(message.encode()).hexdigest()

if __name__ == "__main__":
    # Load and hash the trained dataset
    print("Loading trained dataset...")
    trained_dataset = load_dataset("codeparrot/codeparrot-clean", split="train")
    print("Generating hashes for trained dataset...")
    file_content_hashes_train = {compute_hash_256(content) for content in trained_dataset["content"]}

    # Free memory
    del trained_dataset
    gc.collect()

    # Load dataset to deduplicate
    print("Loading dataset to deduplicate...")
    dataset_to_dedup = load_dataset("bwmfvanveen/repo-dedup_razvan_dataset-codeparrot_clean", split="train")

    dataset_size = len(dataset_to_dedup)
    print(f"Starting with {dataset_size} files to deduplicate")

    # Filter unique files
    files_to_keep = [
        i for i, content in enumerate(dataset_to_dedup["content"])
        if compute_hash_256(content) not in file_content_hashes_train
    ]

    print(f"Found {len(files_to_keep)} unique files.")

    # Select and push deduplicated dataset
    new_dataset = dataset_to_dedup.select(files_to_keep)
    print("Pushing deduplicated dataset to HuggingFace...")

    hf_token = "your_token"
    new_dataset.push_to_hub("nada-mou/ML4SE-exact-dedup-file-final", token=hf_token, private=False)

    print("Deduplication complete!")
