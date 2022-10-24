from __future__ import annotations

import abc
import ast
import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Iterator, List, Tuple, Type

from . import __version__


@dataclass
class Lint:
    line: int
    column: int
    code: str
    message: str


class BasePlugin(abc.ABC):
    version = __version__

    @abc.abstractmethod
    def get_lints(self) -> Iterator[Lint]:
        raise NotImplementedError

    def run(self) -> Iterator[Tuple[int, int, str, Type[Any]]]:
        for lint in self.get_lints():
            yield lint.line, lint.column, f"{lint.code} {lint.message}", type(self)


class AstExaminerPlugin(BasePlugin):
    package: ClassVar[str | None] = None

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree

    def get_lints(self) -> Iterator[Lint]:
        for visitor_type in get_ast_examiners(self.package or type(self).__module__):
            visitor = visitor_type()
            visitor.visit(self.tree)
            yield from visitor.problems


class AstExaminer(ast.NodeVisitor):

    code: ClassVar[str | None] = None
    message: ClassVar[str]

    def __init__(self) -> None:
        self.problems: list[Lint] = []

    def report_problem(self, node: ast.AST) -> None:
        self.problems.append(Lint(node.lineno, node.col_offset, self.code or type(self).__name__, self.message))


def get_ast_examiners(package: str) -> List[Type[AstExaminer]]:
    result = []
    for path in map(Path, importlib.import_module(package).__path__):
        for item in path.iterdir():
            if item.name.endswith(".py") and item.name != "__init__.py":
                module = importlib.import_module(package + "." + item.stem)
                for value in vars(module).values():
                    if isinstance(value, type) and issubclass(value, AstExaminer) and value != AstExaminer:
                        result.append(value)
    return result
