"""

:author: Shay Hill
:created: 7/2/2019

"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_PROJECT = Path(__file__).parent.parent


def pytest_assertrepr_compare(config: Any, op: str, left: str, right: str) -> list[str]:
    """See full error diffs"""
    del config
    if op in ("==", "!="):
        return [f"{left} {op} {right}"]
    return []


RESOURCES = Path(_PROJECT, "tests", "resources")
