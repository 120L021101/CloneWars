# LLM Evaluation 🧪

This directory contains the code for evaluating a model (i.e. CodeParrot) using the `EvalPipeline`.

## Running the Evaluation Pipeline 🏃

Before running the evaluation pipeline, we assume you have already installed the required dependencies.
If not, please refer to the [installation instructions](../README.md).
To run the evaluation pipeline, you can use the following command, while within the root directory of the repository:

```shell
python -m llm_evaluation.main -d <dataset>
```

The `main.py` script is parametrized. Should you toggle the `-h` flag, you will see the following help message:

```
╰─$ python -m llm_evaluation.main -h   
usage: main.py [-h] [--model MODEL] [--dataset DATASET] [--num-samples NUM_SAMPLES] [--verbose]

Evaluate the CodeParrot model on code completion tasks.

options:
  -h, --help            show this help message and exit
  --model MODEL, -m MODEL
                        The model to evaluate on code completion task (CodeParrot default).
  --dataset DATASET, -d DATASET
                        The dataset to evaluate the model on.
  --num-samples NUM_SAMPLES, -n NUM_SAMPLES
                        The number of samples to evaluate the model on.
  --verbose, -v         Increase output verbosity.
```

> **Note**: Unless you are debugging, you will most likely only play around with the `--dataset` parameter.
