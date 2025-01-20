## Outline and setup

Applies exact deduplication on the function level. Hashes functions in the relevant datasets,
checks if it is the first instance of it and if so, saves this instance to our list.

The `util.py` script contains the main relevant information.

## Installation

To install the required dependencies, one needs to follow the instructions in
the [main Installation Section](../README.md#installation-).

## Execution

Run `python util.py` to start exact deduplicating dataset at the function level.

In order to save the data to HuggingFace, input the relevant data at the bottom of the file.
The account token should be the input for the HfApi instance and input your account name in the
push to hub function input.
