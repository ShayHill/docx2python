#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Functions to filter and infer information from attribute dictionaries.

:author: Shay Hill
:created: 3/15/2021

Expect each dictionary to have
Id
Type
Target
dir (added by docx2python)
rels (possibly, for xml files with relationships)
"""
import os
from typing import Dict, Iterator, List, Union

ExpandedAttribDict = Dict[str, Union[str, Dict[str, str], bytes]]


def get_path_rels(path: Dict[str, str]) -> str:
    # TODO: update docstring and ditch previous get_path_rels
    """
    Get path/to/rels for path/to/xml

    :param path: path to a docx content file.
    :returns: path to rels (which may not exist)

    Every content file (``document.xml``, ``header1.xml``, ...) will have its own
    ``.rels`` file--if any relationships are defined.
    """
    dirs = [os.path.dirname(x) for x in (path["dir"], path["Target"])]
    dirname = "/".join([x for x in dirs if x])
    filename = os.path.basename(path["Target"])
    return "/".join([dirname, "_rels", filename + ".rels"])
    # folder, file = os.path.split(path)
    # return "".join([folder, "/_rels/", file, ".rels"])


def get_path(path: Dict[str, str]) -> str:
    # TODO: update docstring and ditch previous get_path_rels
    """
    Get path/to/rels for path/to/xml

    :param path: path to a docx content file.
    :returns: path to rels (which may not exist)

    Every content file (``document.xml``, ``header1.xml``, ...) will have its own
    ``.rels`` file--if any relationships are defined.
    """
    dirs = [os.path.dirname(x) for x in (path["dir"], path["Target"])]
    dirname = "/".join([x for x in dirs if x])
    filename = os.path.basename(path["Target"])
    return "/".join([dirname, filename])
    # folder, file = os.path.split(path)
    # return "".join([folder, "/_rels/", file, ".rels"])


def filter_files_by_type(
    files: List[Dict[str, str]], type_: str
) -> Iterator[Dict[str, str]]:
    """
    Take file objects (rels.attribs) and select with matching type.
    TODO: complete docstring and move to new module

    :param files:
    :return:
    """
    for file in files:
        if os.path.basename(file["Type"]) == type_:
            yield file
