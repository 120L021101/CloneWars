## Outline and setup

These two are set to deduplicate the "Razvan27/ML4SE-Python" dataset. One deduplicates on the file level and the other
deduplicates on the function level.
Both make use of a LSH to evaluate how 'similar' the file/functions are.

Both of these save the resulting data locally and does not upload to huggingface.

Setting up the environment can be done with the commands below.

```
python3.11 -m venv env (linux)
pu -3.11 -m venv env   (windows)

{activate the environment}
python3 -m pip install -r requirements.txt 
```

## Execution

To run the near deduplication at file level locally, execute the following command:

```
python file_dedup.py
```

To run the near deduplication at function level locally, execute the following command:

```
python function_dedup.py
```

In order to change the threshold, the lsh object's input threshold must be changed. The default value is currently set
to 0.65