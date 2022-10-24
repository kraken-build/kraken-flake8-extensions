from textwrap import dedent

from test_utils import get_results

from kraken_flake8_extensions.kraken.kre001 import KRE001
from kraken_flake8_extensions.kraken.kre002 import KRE002


def test__kre001__subscript__default() -> None:
    code = dedent(
        """
        from kraken.core import Property, Task

        class MyTask(Task):
            not_a_prop: list[int]
            good_prop: Property[List[int]]
            bad_prop: Property[list[int]]
    """
    )
    assert get_results(code) == {
        f"5:16 KRE001 {KRE001.message}",
        f"5:16 KRE002 {KRE002.message}",
        f"7:23 KRE001 {KRE001.message}",
        f"7:23 KRE002 {KRE002.message}",
    }


def test__kre001__subscript__future_annotations() -> None:
    code = dedent(
        """
        from __future__ import annotations
        from kraken.core import Property, Task

        class MyTask(Task):
            good_prop: Property[List[int]]
            bad_prop: Property[list[int]]
    """
    )
    assert get_results(code) == {f"7:23 KRE001 {KRE001.message}"}


def test__kre001__subscript__string_literal() -> None:
    code = dedent(
        """
        from kraken.core import Property, Task

        class MyTask(Task):
            good_prop: Property["List[int]"]
            bad_prop: Property["list[int]"]
    """
    )
    assert get_results(code) == {f"6:24 KRE001 {KRE001.message}"}


def test__kre001__type_union__default() -> None:
    code = dedent(
        """
        from __future__ import annotations
        from kraken.core import Property, Task

        class MyTask(Task):
            good_prop: Property[Union[List[str], str]]
            bad_prop: Property[List[str] | str]
    """
    )
    assert get_results(code) == {f"7:23 KRE001 {KRE001.message}"}


def test__kre001__type_union__future_annotations() -> None:
    code = dedent(
        """
        from __future__ import annotations
        from kraken.core import Property, Task

        class MyTask(Task):
            good_prop: Property[Union[List[str], str]]
            bad_prop: Property[List[str] | str]
    """
    )
    assert get_results(code) == {f"7:23 KRE001 {KRE001.message}"}


def test__kre001__type_union__string_literal() -> None:
    code = dedent(
        """
        from kraken.core import Property, Task

        class MyTask(Task):
            good_prop: Property["Union[List[str], str]"]
            bad_prop: Property["List[str] | str"]
    """
    )
    assert get_results(code) == {f"6:24 KRE001 {KRE001.message}"}


def test__kre001__subscript_and_type_union() -> None:
    code = dedent(
        """
        from __future__ import annotations
        from kraken.core import Property, Task

        class MyTask(Task):
            good_prop: Property[Union[List[str], str]]
            bad_prop: Property[list[str] | str]
    """
    )
    assert get_results(code) == {f"7:23 KRE001 {KRE001.message}"}
