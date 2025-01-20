import ast
from typing import List, Tuple


class FunctionExtractor(ast.NodeVisitor):
    def __init__(self, max_depth=1000):
        self.functions = []
        self.current_depth = 0
        self.max_depth = max_depth

    def visit(self, node):
        if self.current_depth > self.max_depth:
            raise RecursionError(
                f"Maximum recursion depth of {self.max_depth} exceeded while parsing AST."
            )

        self.current_depth += 1
        super().visit(node)
        self.current_depth -= 1

    def visit_FunctionDef(self, node):
        try:
            func_code = ast.unparse(node)
            self.functions.append((node.name, func_code))
        except Exception as e:
            self.functions.append((node.name, f"<Error unparsing function: {e}>"))
        self.generic_visit(node)


def extract_functions(source_code: str, max_depth=1000) -> List[Tuple[str, str]]:
    try:
        tree = ast.parse(source_code)
    except:
        return [("<SyntaxError>", f"<Error parsing source code")]
    extractor = FunctionExtractor(max_depth=max_depth)
    try:
        extractor.visit(tree)
    except:
        return [("<RecursionError>")]
    return extractor.functions
