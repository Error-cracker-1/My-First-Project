"""
Function-level Python review helpers for the Daily AI Review project.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import ast


@dataclass(frozen=True)
class FunctionBlock:
    """
    Represents a Python function and its exact source-code range.
    """

    qualname: str
    start_line: int
    end_line: int
    source: str


class _FunctionVisitor(ast.NodeVisitor):
    """
    AST visitor that records functions with qualified names.
    """

    def __init__(self, lines: list[str]):
        self.lines = lines
        self.scope: list[str] = []
        self.functions: list[FunctionBlock] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Track class scope so methods receive stable qualified names.
        """

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Record regular functions and continue into nested functions.
        """

        self._record_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Record async functions and continue into nested functions.
        """

        self._record_function(node)

    def _record_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        """
        Store a function block using decorator-aware line numbers.
        """

        start_line = node.lineno

        if node.decorator_list:
            start_line = min(
                decorator.lineno
                for decorator in node.decorator_list
            )

        end_line = node.end_lineno or node.lineno
        qualname = ".".join([*self.scope, node.name])
        source = "".join(
            self.lines[start_line - 1:end_line]
        )

        self.functions.append(
            FunctionBlock(
                qualname=qualname,
                start_line=start_line,
                end_line=end_line,
                source=source,
            )
        )

        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()


def extract_functions(content: str) -> list[FunctionBlock]:
    """
    Parse Python source and return every function block.

    SyntaxError is intentionally allowed to bubble up so callers can fall back
    to whole-file review when the AST cannot be parsed.
    """

    tree = ast.parse(content)
    lines = content.splitlines(keepends=True)
    visitor = _FunctionVisitor(lines)
    visitor.visit(tree)

    return visitor.functions


def read_head_version(path: Path) -> str | None:
    """
    Read a tracked file from HEAD for change comparison.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "show",
                f"HEAD:{path.as_posix()}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    except Exception:
        return None

    return result.stdout


def compare_functions(
    base_content: str,
    current_content: str,
) -> list[FunctionBlock]:
    """
    Return functions whose source changed between base and current content.
    """

    base_functions = {
        function.qualname: function.source
        for function in extract_functions(base_content)
    }

    changed_functions = []

    for function in extract_functions(current_content):
        if base_functions.get(function.qualname) != function.source:
            changed_functions.append(function)

    return changed_functions


def merge_updated_functions(
    original_content: str,
    changed_functions: list[FunctionBlock],
    updated_functions: dict[str, str],
) -> str:
    """
    Replace reviewed functions while preserving all other bytes exactly.
    """

    lines = original_content.splitlines(keepends=True)

    # Replace from the bottom up so earlier line ranges remain valid.
    for function in sorted(
        changed_functions,
        key=lambda item: item.start_line,
        reverse=True,
    ):
        updated_source = updated_functions.get(function.qualname)

        if updated_source is None:
            continue

        original_source = "".join(
            lines[function.start_line - 1:function.end_line]
        )

        if original_source.endswith("\n") and not updated_source.endswith("\n"):
            updated_source += "\n"

        lines[function.start_line - 1:function.end_line] = [
            updated_source
        ]

    return "".join(lines)
