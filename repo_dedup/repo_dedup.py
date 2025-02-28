from datasets import load_dataset
from huggingface_hub import HfApi


def dedup_from_repo(dedup_dataset, dedup_col_name, trained_dataset, trained_col_name, dedup_dataset_name="", trained_dataset_name=""):
    """Deduplicates a dataset based on repository names from a trained dataset."""
    
    # Load datasets
    dataset_to_dedup = load_dataset(dedup_dataset)
    trained_dataset = load_dataset(trained_dataset)

    # Extract repository names from trained dataset
    used_repo_set = set(trained_dataset["train"][trained_col_name])

    # Filter out duplicates
    valid_list = [i for i, repo_name in enumerate(dataset_to_dedup["train"][dedup_col_name]) if repo_name not in used_repo_set]

    # Select deduplicated dataset
    new_dataset = dataset_to_dedup["train"].select(valid_list)

    # Push the deduplicated dataset to Hugging Face Hub
    api = HfApi(token="")
    dataset_hub_name = f"bwmfvanveen/repo-dedup_{dedup_dataset_name}-{trained_dataset_name}"
    new_dataset.push_to_hub(dataset_hub_name, token=api.token)

    print(f"Deduplicated dataset pushed to {dataset_hub_name}")


if __name__ == "__main__":
    dedup_from_repo(
        dedup_dataset="Razvan27/ML4SE-Python",
        dedup_col_name="repo_name",
        trained_dataset="codeparrot/codeparrot-clean",
        trained_col_name="repo_name",
        dedup_dataset_name="razvan_dataset",
        trained_dataset_name="codeparrot_clean"
    )

    print("Deduplication completed.")
