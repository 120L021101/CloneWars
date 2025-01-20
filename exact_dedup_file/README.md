# Exact Deduplication at File Level

To run the exact deduplication at file level on Delft Blue, execute the following command:
```sh
sbatch job.sh
```

To run the exact deduplication at file level locally, execute the following command:

```sh
python util.py
```

If you want to also publish the results of deduplication at file level, you can utilize the `push_to_hugging_face.py`
script. This script is parametrized and has the following usage:

```
usage: push_to_hugging_face.py [-h] --local-repo-name LOCAL_REPO_NAME --hf-repo-name HF_REPO_NAME --hf-token HF_TOKEN

Push the deduplicated dataset to Hugging Face.

options:
  -h, --help            show this help message and exit
  --local-repo-name LOCAL_REPO_NAME, -l LOCAL_REPO_NAME
                        The path to the local dataset repository.
  --hf-repo-name HF_REPO_NAME, -r HF_REPO_NAME
                        The name of the Hugging Face repository.
  --hf-token HF_TOKEN, -t HF_TOKEN
                        The Hugging Face token.
```
