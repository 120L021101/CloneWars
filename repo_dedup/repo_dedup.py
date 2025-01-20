from datasets import load_dataset
from huggingface_hub import HfApi


# dedup_dataset  is the dataset we want to deduplicate in the end.
# dedup_col_name is the 'repo name' equivalent of the dataset which we are deduplicating
# trained_dataset  is the dataset we have presumably trained on and want no repo duplicates of in the end.
# trained_col_name is the 'repo name' equivalent of the dataset which we have trained from
def dedup_from_repo(dedup_dataset, dedup_col_name, trained_dataset, trained_col_name, dedup_dataset_name="", trained_dataset_name=""):
    dataset_to_dedup = load_dataset(dedup_dataset)
    trained_dataset = load_dataset(trained_dataset)

    # I'm just going to assume they all have 'train' tbh
    used_repo_set = set(trained_dataset['train'][trained_col_name])

    index = 0
    valid_list = []
    for current_repo_name in dataset_to_dedup['train'][dedup_col_name]:
        if current_repo_name not in used_repo_set:
            valid_list.append(index)
        index += 1

    new_dataset = dataset_to_dedup['train'].select(valid_list)

    # You're going to need permission to push to my HF, if you want to use this use an access token and your own HF and it should be fine
    api = HfApi(token="")
    new_dataset.push_to_hub(f"bwmfvanveen/repo-dedup_{dedup_dataset_name}-{trained_dataset_name}", token=api.token)



if __name__ == '__main__':
    dedup_dataset = "Razvan27/ML4SE-Python"
    dedup_col_name = "repo_name"
    trained_dataset = "codeparrot/codeparrot-clean"
    trained_col_name = "repo_name"

    # These two are just for saving to HF purposes
    dedup_dataset_name = "razvan_dataset"
    trained_dataset_name = "codeparrot_clean"
    dedup_from_repo(dedup_dataset, dedup_col_name, trained_dataset, trained_col_name, dedup_dataset_name, trained_dataset_name)

    print("done")