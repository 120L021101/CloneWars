import json
import logging
import os

import tree_sitter_python
from transformers import AutoTokenizer
from tree_sitter import Language, Parser

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class PreProcessing:
    """
    This is the class responsible for pre-processing the dataset of Python files into (context, groundtruth) samples.
    """

    def __init__(self, dataset, model, verbose=False):
        self.dataset = dataset
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.verbose = verbose

        # Initialize Tree-sitter parser for Python
        PYTHON_LANGUAGE = Language(tree_sitter_python.language())
        self.parser = Parser(PYTHON_LANGUAGE)

    def parse_code(self, file_content):
        """
        Initialize the tree structure representing a given code file
        """
        tree = self.parser.parse(bytes(file_content, "utf8"))
        return tree.root_node

    def extract_functions_with_docstrings_recursive(
        self, node, code, parent_context="", max_functions=3, extracted_count=0
    ):
        """
        Recursively extract functions with docstrings from the AST which
        my includes functions inside classes or nested structures.

        Args:
            node: The current AST node to process.
            code: The full source code of the file.
            parent_context: Context inherited from parent nodes (e.g., class definitions).
        Returns:
            A list of dictionaries containing function data (function_name, context, groundtruth).
        """
        functions = []

        # Iterate through the children of the current node
        for child in node.children:

            # Stop recursion if we've already extracted the maximum number of functions
            if extracted_count >= max_functions:
                break

            if child.type == "function_definition":
                # Extract the function name
                name_node = child.child_by_field_name("name")
                function_name = code[name_node.start_byte : name_node.end_byte].strip()
                full_function_name = (
                    f"{parent_context}.{function_name}"
                    if parent_context
                    else function_name
                )
                if self.verbose:
                    logger.info(f"Function name: {full_function_name}")
                # Extract the body of the function
                body_node = child.child_by_field_name("body")
                if body_node and len(body_node.children) > 0:
                    first_child = body_node.children[0]
                    # Check if the first child is an expression_statement containing a string (docstring)
                    if (
                        first_child.type == "expression_statement"
                        and first_child.child(0).type == "string"
                    ):
                        docstring_node = first_child.child(0)
                        # Extract context (up to and including the docstring)
                        start = 0  # Context starts from the beginning of the file
                        end = docstring_node.end_byte  # End at the end of the docstring
                        context = code[start:end].strip()

                        # Extract function body (after the docstring)
                        function_body_start = (
                            body_node.children[1].start_byte
                            if len(body_node.children) > 1
                            else docstring_node.end_byte
                        )
                        function_body = code[
                            function_body_start : child.end_byte
                        ].strip()

                        # Append function details
                        functions.append(
                            {
                                "function_name": full_function_name,
                                "context": context,
                                "groundtruth": function_body,
                            }
                        )
                        extracted_count += 1

            elif child.type == "class_definition":
                # Extract the class name
                class_name_node = child.child_by_field_name("name")
                class_name = code[
                    class_name_node.start_byte : class_name_node.end_byte
                ].strip()
                new_parent_context = (
                    f"{parent_context}.{class_name}" if parent_context else class_name
                )

                # Recursively process the class body
                class_body_node = child.child_by_field_name("body")
                if class_body_node:
                    if extracted_count < max_functions:
                        functions.extend(
                            self.extract_functions_with_docstrings_recursive(
                                class_body_node,
                                code,
                                parent_context=new_parent_context,
                                max_functions=max_functions,
                                extracted_count=extracted_count,
                            )
                        )
                        extracted_count = len(functions)

            if extracted_count < max_functions:
                # Recursively process other nested structures (e.g., nested functions)
                functions.extend(
                    self.extract_functions_with_docstrings_recursive(
                        child,
                        code,
                        parent_context,
                        max_functions=max_functions,
                        extracted_count=extracted_count,
                    )
                )
                extracted_count = len(functions)

        return functions[:max_functions]

    def tokenize_and_filter(self, context, groundtruth):
        """
        Tokenize the context and groundtruth, and apply length constraints.
        """
        context_max = 768
        gt_max = 256
        context_tokens = self.tokenizer.encode(context, truncation=True)
        groundtruth_tokens = self.tokenizer.encode(groundtruth, truncation=True)

        # Check if groundtruth exceeds the allowed limit
        if len(groundtruth_tokens) > gt_max:
            return None, None

        # If the context is too long, trim the beginning
        if len(context_tokens) > context_max:
            excess_tokens = len(context_tokens) - context_max
            trimmed_context_tokens = context_tokens[excess_tokens:]
            return trimmed_context_tokens, groundtruth_tokens

        return context_tokens, groundtruth_tokens

    def process_file(self, file_path, code):
        """
        Process a single Python file to extract inputs for code completion task:
        - file_path+function_name
        - the context
        - the groundtruth
        - context_length and groundtruth_length for stats
        """
        root_node = self.parse_code(code)
        functions = self.extract_functions_with_docstrings_recursive(
            root_node, code, max_functions=3, extracted_count=0
        )
        dataset = []

        for func in functions:
            function_name = func["function_name"]
            context = func["context"]
            groundtruth = func["groundtruth"]
            context_tokens, groundtruth_tokens = self.tokenize_and_filter(
                context, groundtruth
            )
            if context_tokens and groundtruth_tokens:
                # Convert back to text for the dataset
                trimmed_context = self.tokenizer.decode(
                    context_tokens, skip_special_tokens=True
                )
                dataset.append(
                    {
                        "id": f"{file_path}_{function_name}",
                        "context": trimmed_context,
                        "groundtruth": groundtruth,
                        "context_length": len(context_tokens),
                        "groundtruth_length": len(groundtruth_tokens),
                    }
                )

        return dataset

    def preprocess_dataset(self):
        """
        Extract Python files from the database and process them.
        """
        preprocessed_data = []
        content = self.dataset["content"]
        file_name = self.dataset["file_name"]

        i = 0
        for context, path_name in zip(content, file_name):

            if i % 1000 == 0:
                logger.info(f"Processing files {i / len(self.dataset) * 100:.2f}%")

            if context and path_name:
                if os.path.splitext(path_name)[1] == ".py":
                    preprocessed_data.extend(self.process_file(path_name, context))
            i += 1

        # with open("code_completion_dataset.jsonl", "w") as f:
        #     for entry in preprocessed_data:
        #         f.write(json.dumps(entry) + "\n")

        return preprocessed_data
