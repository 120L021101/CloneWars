import argparse
import logging
import os
from datasets import Dataset

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def push_to_hf(local_repo_name: str, hf_repo_name: str, hf_token: str) -> None:
    """
    Pushes the provided dataset to a specified Hugging Face repository.
    :param local_repo_name: the path to the local dataset repository
    :param hf_repo_name: the name of the Hugging Face repository
    :param hf_token: the Hugging Face token
    :return: None
    """

    dataset = Dataset.load_from_disk(local_repo_name)
    dataset.push_to_hub(repo_id=hf_repo_name, token=hf_token, private=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Push the deduplicated dataset to Hugging Face."
    )

    parser.add_argument(
        "--local-repo-name",
        "-l",
        type=str,
        required=True,
        default="/scratch/nmouman/deduped_data/ML4SE/ML4SE-file-final",
        help="The path to the local dataset repository.",
    )

    parser.add_argument(
        "--hf-repo-name",
        "-r",
        type=str,
        required=True,
        help="The name of the Hugging Face repository.",
    )

    parser.add_argument(
        "--hf-token", "-t", type=str, required=True, help="The Hugging Face token."
    )

    # Parse the arguments
    args = parser.parse_args()
    local_repo = args.local_repo_name
    hf_repo = args.hf_repo_name
    hf_api_token = args.hf_token

    # Input Validation
    if not os.path.exists(local_repo):
        raise ValueError("Please specify a valid path to the local dataset repository.")

    # Push the deduplicated dataset to Hugging
    push_to_hf(local_repo_name=local_repo, hf_repo_name=hf_repo, hf_token=hf_api_token)

    # Default example
    # push_to_hf(
    #     local_repo_name="/scratch/nmouman/deduped_data/ML4SE/ML4SE-file-final",
    #     hf_repo_name="nada-mou/ML4SE-exact-dedup-file",
    #     hf_token="your_token"
    # )
