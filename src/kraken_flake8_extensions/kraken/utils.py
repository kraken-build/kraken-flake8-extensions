from __future__ import annotations

import ast

import astor  # type: ignore[import]


def parse_string_annotation(node: ast.Constant) -> ast.AST:
    assert isinstance(node.value, str), type(node.value)
    new_node = ast.parse(
        node.value,
        filename=f"<annotation on {node.lineno}:{node.col_offset}>",
        mode="eval",
    ).body
    new_node = ast.copy_location(new_node, node)
    new_node.col_offset += 1
    return new_node


def is_kraken_core_property_object_subclass(node: ast.ClassDef) -> bool:
    # TODO(niklas.rosenstein): We should do a better analysis here to see if the base class is actually
    #       a subclass of `kraken.core.property.Object` to enable/disable the linting. This heuristic will
    #       fail over easily.
    for base in node.bases:
        if astor.to_source(base).strip().endswith("Task"):
            return True
    return False
