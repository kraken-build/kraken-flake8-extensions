import ast
from typing import Set

from kraken_flake8_extensions.kraken import Flake8KrakenPlugin


def get_results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Flake8KrakenPlugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}
