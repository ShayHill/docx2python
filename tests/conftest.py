"""See full diffs in pytest.

:author: Shay Hill
:created: 2019-07-02
"""

from pathlib import Path

import pytest

_PROJECT = Path(__file__).parent.parent


def pytest_assertrepr_compare(
    config: pytest.Config, op: str, left: str, right: str
) -> list[str] | None:
    """See full error diffs"""
    del config
    if op in ("==", "!="):
        return [f"{left} {op} {right}"]
    return None


RESOURCES = _PROJECT / "tests" / "resources"
