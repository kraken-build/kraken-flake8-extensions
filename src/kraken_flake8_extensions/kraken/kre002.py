from __future__ import annotations

import ast
from itertools import chain
from typing import Any

from kraken_flake8_extensions.base import AstExaminer

from .kre001 import FLAG_SUBSCRIPT_ON_THESE_NAMES


class KRE002(AstExaminer):

    message = (
        "Use of built-in type subscripts (3.9+) or type unions (3.10+) requires `from __future__ import annotations` "
        "for backwards compatibility."
    )

    def __init__(self) -> None:
        super().__init__()
        self._has_annotations_import = False
        self._state: list[str] = []

    def _get_state(self) -> str | None:
        return self._state[-1] if self._state else None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module == "__future__" and any(alias.name == "annotations" for alias in node.names):
            self._has_annotations_import = True

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        if not self._has_annotations_import and self._get_state() == "ANNOTATION":
            if isinstance(node.value, ast.Name) and node.value.id in FLAG_SUBSCRIPT_ON_THESE_NAMES:
                self.report_problem(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        self._state.append("ANNOTATION")
        self.visit(node.annotation)
        self._state.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        for arg in chain(
            node.args.args,
            [node.args.vararg] if node.args.vararg else [],
            node.args.kwonlyargs,
            [node.args.kwarg] if node.args.kwarg else [],
        ):
            if arg.annotation:
                self._state.append("ANNOTATION")
                self.visit(arg.annotation)
                self._state.pop()

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        self.generic_visit(node)
        if isinstance(node.op, ast.BitOr) and self._get_state() == "ANNOTATION" and not self._has_annotations_import:
            self.report_problem(node)
