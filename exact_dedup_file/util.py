import gc
import hashlib

from datasets import load_dataset


def compute_hash_256(message):
    return hashlib.sha256(message.encode()).hexdigest()


if __name__ == "__main__":

    # Load the trained dataset
    trained_dataset = load_dataset("codeparrot/codeparrot-clean")

    print("Getting file content for trained dataset...")
    file_content_trained_dataset = set(trained_dataset["train"]["content"])

    print("Generating hashes for trained dataset...")
    file_content_hashes_train = set(
        compute_hash_256(content) for content in file_content_trained_dataset
    )

    # Dump the trained dataset to free up memory
    del file_content_trained_dataset
    del trained_dataset
    gc.collect()

    # Load the dataset to deduplicate
    dataset_to_dedup = load_dataset(
        "bwmfvanveen/repo-dedup_razvan_dataset-codeparrot_clean"
    )

    dataset_size = len(dataset_to_dedup["train"])

    print(f"Starting with {dataset_size} files to deduplicate")

    i = 0
    files_to_keep = []

    for current_file_content in dataset_to_dedup["train"]["content"]:
        hashed_content = compute_hash_256(current_file_content)

        if i % 1000 == 0:
            print(
                f"Processing item {i + 1}/{dataset_size} ({(i + 1) / dataset_size * 100:.2f}%), Unique files: {len(files_to_keep)}"
            )

        # Keep the file if it's not in the trained dataset by comparing hash
        if hashed_content not in file_content_hashes_train:
            files_to_keep.append(i)

        i += 1

    new_dataset = dataset_to_dedup["train"].select(files_to_keep)

    print(f"Pushing to HuggingFace new deduped dataset...")

    # Push the deduplicated dataset to HuggingFace
    hf_token = "your_token"
    new_dataset.push_to_hub(
        "nada-mou/ML4SE-exact-dedup-file-final", token=hf_token, private=False
    )

    print(f"Deduplicated dataset saved with {len(files_to_keep)} unique files!")
