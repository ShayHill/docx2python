#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""

:author: Shay Hill
:created: 7/2/2019

"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

def pytest_assertrepr_compare(config, op, left, right):
    # see full error diffs
    if op in ('==', '!='):
        return ['{0} {1} {2}'.format(left, op, right)]