#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""

:author: Shay Hill
:created: 7/2/2019

"""

import os
import sys
from pathlib import Path

project = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.append(project)


def pytest_assertrepr_compare(config, op, left, right):
    """See full error diffs"""
    if op in ("==", "!="):
        return ["{0} {1} {2}".format(left, op, right)]


RESOURCES = Path(project, "test", "resources")
