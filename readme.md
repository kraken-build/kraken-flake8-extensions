# kraken-flake8-extensions

This Flake8 plugin implements lints specific for the code base of the Kraken build system.

| Code | Description |
| ---- | ----------- |
| `KRE001` | Annotations on `kraken.core.property.Object` subclasses (such as tasks) must use backwards compatible type hints because they are evaluated at runtime. Use collection types from the `typing` module instead. |
| `KRE002` | Use of built-in type subscripts (3.9+) or type unions (3.10+) requires `from __future__ import annotations` for backwards compatibility. |
