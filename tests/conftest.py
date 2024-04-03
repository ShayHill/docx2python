"""

:author: Shay Hill
:created: 7/2/2019

"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

project = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.append(project)


def pytest_assertrepr_compare(config: Any, op: str, left: str, right: str) -> list[str]:
    """See full error diffs"""
    del config
    if op in ("==", "!="):
        return [f"{left} {op} {right}"]
    return []


RESOURCES = Path(project, "tests", "resources")
