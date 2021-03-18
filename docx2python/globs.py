#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Global variables for docx context.

:author: Shay Hill
:created: 3/18/2021

The rels and flags for docx processing.
# TODO: improve docmod
"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DocxContext:
    # each xml file has its own rels file.
    # rId numbers are NOT unique between rels files.
    # update this value before parsing text for each xml content file.
    current_file_rels: Dict[str, Dict[str, str]] = field(default_factory=dict)
