from __future__ import annotations

import ast
from typing import Any

from kraken_flake8_extensions.base import AstExaminer
from kraken_flake8_extensions.kraken.utils import is_kraken_core_property_object_subclass, parse_string_annotation

FLAG_SUBSCRIPT_ON_THESE_NAMES = ("dict", "frozenset", "list", "tuple", "set")


class KRE001(AstExaminer):

    message = (
        "Annotations on `kraken.core.property.Object` subclasses (such as tasks) must use backwards compatible type "
        "hints because they are evaluated at runtime. Use the `typing` module instead of subscripting built-in types "
        "(3.9+) or type unions (3.10+)."
    )

    def __init__(self) -> None:
        super().__init__()
        self._state: list[str] = []

    def _get_state(self) -> str | None:
        return self._state[-1] if self._state else None

    def visit_Constant(self, node: ast.Constant) -> Any:
        """If we encounter a string inside an annotation, we parse it as well."""

        if isinstance(node.value, str) and self._get_state() == "ANNOTATION":
            new_node = parse_string_annotation(node)
            self.visit(new_node)
        else:
            self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        if is_kraken_core_property_object_subclass(node):
            self._state.append("SUBCLASS")
            self.generic_visit(node)
            self._state.pop()
        else:
            self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        if self._get_state() == "SUBCLASS":
            self._state.append("ANNOTATION")
            self.visit(node.annotation)
            self._state.pop()
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._state.append("")
        self.generic_visit(node)
        self._state.pop()

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        if self._get_state() == "ANNOTATION":
            if isinstance(node.value, ast.Name) and node.value.id in FLAG_SUBSCRIPT_ON_THESE_NAMES:
                self.report_problem(node)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        self.generic_visit(node)
        if isinstance(node.op, ast.BitOr) and self._get_state() == "ANNOTATION":
            self.report_problem(node)
