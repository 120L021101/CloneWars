# ML4SE Deduplication Exploration Project - Group 14

This repository contains the project work done for
the [CS4570 Machine Learning for Software Engineering](https://studiegids.tudelft.nl/a101_displayCourse.do?course_id=70144)
Master's course at TU Delft. More specifically our team chose the project on:

> _Examine how different code deduplication levels (exact/near/semantic) impact LLM performance in code tasks.
One extension would be to look into different MinHashLSH configurations compared
to the standard setup used in most papers (Stack, StarCoder, and Allamanis’ paper)._

## Installation 🚀

1. **Install Python >= 3.9**:
    - Install Python from the [official website](https://www.python.org/downloads/).
    - Ensure that Python is added to the system PATH.
    - Preferably, use a virtual environment to install the required packages (if not, skip to step 3).
    - Most dependencies require Python 3.9 or higher.
2. **Create & Activate Virtual Environment**
    - **On Unix-based Systems**:
        - Confirm that you have Python 3 installed (Note: you can also just check this with `python --version`):
          Depending on the version/binary you have installed, either of the following commands should work,
          which will return the path to the python binary (e.g., `/usr/bin/python3` if it exists):
          ```sh
          which python3
          # or
          which python
          # or
          which python3.9
          ```
        - Go to the root directory of the project.
        - Create a virtual environment:
            ```sh
            python3 -m venv .venv
            ```
        - Activate the virtual environment:
          ```sh
          source .venv/bin/activate
          ```
        - In case you may want to deactivate the virtual environment, at any time run:
          ```sh
            deactivate
         ```
    - **On Windows**:
        - Confirm you have Python installed either via `where python` or `python --version`.
        - The rest of the steps should be identical to Unix-based systems.
3. **Go to the module you want to work with/in**:
    - `cd <module_name>` (e.g., `cd llm_evaluation`)
4. **Install Python Package Requirements**:

  ```sh
  pip install -r requirements.txt
  ```

## Project Structure 🏗️

This project has multiple modules that have been used for different tasks. More specifically:

* `exact_dedup_file`: Contains the code for running the exact deduplication at file
  level ([README.md](exact_dedup_file/README.md)).
* `exact_dedup_function`: Contains the code for running the exact deduplication at function
  level [README.md](exact_dedup_function/README.md).
* `llm_evaluation`: Contains the code for running the evaluation pipeline [README.md](llm_evaluation/README.md).
* `near_dedup_function`: Contains the code for near deduplication on both the file and function
  levels. [README.md](near_dedup_function/README.md)
* `repo_dedup`: Contains the code to deduplicate at a repository level compared to a given training
  dataset. [README.md](repo_dedup/README.md)
* `data_scraper`: Contains code used to scrape GitHub repositories to test against. [README.md](data_scraper/README.md)

> Note that each module has its own `README` file that explains how to run the code and more details about the module.
> As explained in the [Installation](#installation-) section, each module also has its own `requirements.txt` file.

## Code Quality Checks 🧹

To ensure consistent code quality, we use the following tools:

1. **Black (Code Formatter)** - See [Black Documentation](https://black.readthedocs.io/en/stable/)
2. **Isort (Import Sorter)** - See [Isort Documentation](https://pycqa.github.io/isort/)

We advise running the following commands while in the root directory of this repository before committing any changes:

1. `pip install -r requirements.txt` (if not already done when setting up the project)
2. `black --check .` (to check if the code is formatted correctly)
    - If the above fails, run `black .` to automatically format the code.
3. `isort --check-only .` (to check if the imports are sorted correctly)
    - If the above fails, run `isort .` to automatically sort the imports.

> **Note**: The above `black` & `isort` checks are not enforced in the CI pipeline at the moment.
> This is because in some instances, these tools may have conflicts with each other.
> Moreover, we also recommend using `pylint` for static code analysis, but we do not enforce it either.
