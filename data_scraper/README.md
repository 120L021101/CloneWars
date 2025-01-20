# Intro & Basic Setup

The data scraped as part of this module was not used in the end, but the scraper is still functional.
It goes through each folder in the repository to look for relevant files and save them to a database.
It then saves the scraped data to a huggingface dataset, though you will need to supply that yourself.

Before running the scraper, you will need to follow the instructions within
the [Installation part of the main README.md](../README.md#installation-).

## Scraper execution

In `scraper.py` you can change the repositories which are scraped individually by running the `scrape_repository`
function from main. You can also scrape a large series of repositories from the top ~7700 highest rated repos by
inserting the amount you want to scrape (and optionally the offset position to start at).

The `scraper.py` can be parametrized. These are the following parameters:

```
usage: scraper.py [-h] [--upload] [--repo REPO] [--dataset DATASET]

Scrape the top repositories on GitHub and save them to a database.

options:
  -h, --help            show this help message and exit
  --upload, -u          Toggle whether to upload the scraped data to HuggingFace.
  --repo REPO, -r REPO  The HuggingFace repo to upload the dataset to.
  --dataset DATASET, -d DATASET
                        The path for the dataset to upload to HuggingFace.
```

For example, if you want to scrape the predefined amount of repositories and upload them to HuggingFace, you can run:

```sh
python scraper.py --upload --repo <your_huggingface_repo> --dataset <your_dataset_path>
```

> Note: By default, the scraper will not upload the data to HuggingFace. However, if you enable this, note that
> the default dataset path is `scraped_repos.db` and the default HuggingFace repository is
> `bwmfvanveen/ml4se-team14-bigger-scraped-dataset` (which is a dataset that is already exists so you probably want
> to change this).

## Saving to HF

If you want to save the scraped data to HuggingFace, you can use the `upload_db.py` script. Most likely, this script
should be executed if you did not upload the data to HuggingFace during the scraping process. The script is also
parametrized, and these are the following parameters:

```
usage: upload_db.py [-h] [--repo REPO] [--dataset DATASET] --token TOKEN

Upload the scrapped repos dataset to HuggingFace.

options:
  -h, --help            show this help message and exit
  --repo REPO, -r REPO  The HuggingFace repo to upload the dataset to.
  --dataset DATASET, -d DATASET
                        The path for the dataset to upload to HuggingFace.
  --token TOKEN, -t TOKEN
                        The HuggingFace API token.
```

For example, if you want to upload the `scraped_repos.db` dataset to HuggingFace, under the repository
titled `ml4se-team14/scraped-repos`, you can run:

```sh
python upload_db.py --repo ml4se-team14/scraped-repos --dataset scraped_repos.db --token <your_huggingface_token>
```

As previously mentioned, an example of a dataset with 40k rows scraped using `scraper.py` can be found
at: https://huggingface.co/datasets/bwmfvanveen/ml4se-team14-bigger-scraped-dataset
