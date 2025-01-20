import argparse
import logging
import os

from datasets import Dataset, Features, Value
from huggingface_hub import HfApi

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def save_to_hf(hf_repo: str, dataset_path: str, hf_token: str):
    """
    Save the scraped repos to HuggingFace.
    :param hf_repo: The HuggingFace repo to upload the dataset to.
    :param dataset_path: The path for the dataset to upload to HuggingFace.
    :param hf_token: The HuggingFace API token.
    :return: None
    """

    logger.info("Starting process of saving to huggingface...")

    # Set up the HuggingFace API (If token was not provided correctly, this will raise an error)
    api = HfApi(token=hf_token)

    # URI to connect to the created scraped_repos db we set up in the scraper
    uri = f"sqlite:///{dataset_path}"

    # Features for the db table that was set up by default
    context_feat = Features(
        {
            "ID": Value(dtype="uint32"),
            "Repo_Name": Value(dtype="string", id=None),
            "Branch": Value(dtype="string", id=None),
            "Path": Value(dtype="string", id=None),
            "Date_Scraped": Value(dtype="date32", id=None),
            "Language_ID": Value(dtype="string", id=None),
            "Data": Value(dtype="large_string", id=None),
        }
    )

    # Simply load the scraped pages table from database and then push it to the huggingface repo.
    ds = Dataset.from_sql(
        "SCRAPED_PAGE", con=uri, cache_dir="hugCache", features=context_feat
    )

    ds.push_to_hub(hf_repo, token=api.token)
    logger.info("Successfully saved dataset to HuggingFace")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload the scrapped repos dataset to HuggingFace."
    )

    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        required=False,
        default="bwmfvanveen/ml4se-team14-bigger-scraped-dataset",
        help="The HuggingFace repo to upload the dataset to.",
    )

    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        required=False,
        default="scraped_repos.db",
        help="The path for the dataset to upload to HuggingFace.",
    )

    parser.add_argument(
        "--token", "-t", type=str, required=True, help="The HuggingFace API token."
    )

    # Parse the arguments
    args = parser.parse_args()
    hf_repository = args.repo
    db_path = args.dataset
    hf_api_token = args.token

    # Input Validation
    if db_path is None:
        raise ValueError("Please specify the dataset to upload to HuggingFace.")
    if not os.path.exists(db_path):
        raise ValueError("The dataset path provided does not exist.")

    save_to_hf(hf_repository, db_path, hf_api_token)
