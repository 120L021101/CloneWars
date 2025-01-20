## Outline and setup

This is a simple function to perform deduplication on the reposiory level between a target dataset and a trained
dataset.
The target dataset has any files taken from repositories which overlap with the trained dataset removed.

```
python3.11 -m venv env (linux)
pu -3.11 -m venv env   (windows)

{activate the environment}
python3 -m pip install -r requirements.txt 

# alternatively, you can just run pip install datasets or use an env from any of 
# the other dedup functions
```

## Execution

In the repo_dedup file, insert the appropriate hf datasets into the dedup/trained_dataset inputs,
and insert the appropriate column names which include the repository names.

Insert HF requirements such as token and desired dataset name

After that simply execute

```
python repo_dedup.py
```