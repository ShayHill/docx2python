#!/usr/bin/env python3
# last modified: 211221 19:20:29
"""Utility / example functions using new (as of 2.0.0 Docx2Python features)

:author: Shay Hill
:created: 2021-12-21

Docx2Python version two exposes extracted xml in the DocxReader object and has a new
paragraph_styles argument. These functions use these new features as utilities /
examples.
"""

import re
from pathlib import Path
from typing import Iterator, List, Tuple, Union

from lxml import etree

from .iterators import iter_at_depth
from .main import docx2python


def replace_root_text(root: etree._Element, old: str, new: str) -> None:
    """Replace :old: with :new: in all descendants of :root:

    :param root: an etree element presumably containing descendant text elements
    :param old: text to be replaced
    :param new: replacement text
    """
    for text_elem in (x for x in root.iter() if x.text):
        text_elem.text = (text_elem.text or "").replace(old, new)


def replace_docx_text(
    path_in: Union[Path, str],
    path_out: Union[Path, str],
    *replacements: Tuple[str, str],
    html: bool = False
) -> None:
    """Replace text in a docx file.

    :param path_in: path to input docx
    :param path_out: path to output docx with text replaced
    :param replacements: tuples of strings (a, b) replace a with b for each in docx.
    :param html: respect formatting (as far as docx2python can see formatting)
    """
    reader = docx2python(path_in, html=html).docx_reader
    for file in reader.content_files():
        root = file.root_element
        for replacement in replacements:
            replace_root_text(root, *replacement)
    reader.save(path_out)
    return


def get_links(path_in: Union[Path, str]) -> Iterator[Tuple[str, str]]:
    """Iter links inside a docx file as (href, text)

    :param path_in: path to input docx
    :yields: every link in the file as a tuple of (href, text)
    """
    link_pattern = re.compile('<a href="(?P<href>[^"]+)">(?P<text>[^<]+)</a>')
    extraction = docx2python(path_in)
    for run in iter_at_depth(extraction.document_runs, 5):
        match = re.match(link_pattern, run)
        if match:
            href, text = match.groups()
            yield href, text


def get_headings(path_in: Union[Path, str]) -> Iterator[List[str]]:
    """Iter paragraphs with 'Heading' patagraph_style

    :param path_in: path to input docx

    When docx2python paragraph_styles parameter is set to True, the first run in
    every paragraph will be a paragraph style extracted from the xml, if present.
    Else, paragraphs style will be "".
    """
    heading_pattern = re.compile(r"Heading\d")
    extraction = docx2python(path_in, paragraph_styles=True).document_runs
    for par in iter_at_depth(extraction, 4):
        if re.match(heading_pattern, par[0]):
            yield par
