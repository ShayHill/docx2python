"""Utility / example functions using new (as of 2.0.0 Docx2Python features).

:author: Shay Hill
:created: 2021-12-21

Docx2Python version two exposes extracted xml in the DocxReader object and has a new
paragraph_styles argument. These functions use these new features as utilities /
examples.
"""

from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING, Iterator

from lxml import etree

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python

if TYPE_CHECKING:

    import os

    from lxml.etree import _Element as EtreeElement  # type: ignore


def _copy_new_text(elem: EtreeElement, new_text: str) -> EtreeElement:
    """Copy a text element and replace text.

    :param elem: an etree element with tag w:t
    :param new_text: text to replace elem.text
    :return: a new etree element with tag w:t and text new_text
    """
    new_elem = copy.deepcopy(elem)
    new_elem.text = new_text
    return new_elem


def _new_br_element(elem: EtreeElement) -> EtreeElement:
    """Return a break element with a representative elements namespace.

    :param elem: xml element
    :return: a new br element
    """
    prefix = elem.nsmap["w"]
    return etree.Element(f"{{{prefix}}}br")


def replace_root_text(root: EtreeElement, old: str, new: str) -> None:
    """Replace :old: with :new: in all descendants of :root:.

    :param root: an etree element presumably containing descendant text elements
    :param old: text to be replaced
    :param new: replacement text

    Will use softbreaks <br> to preserve line breaks in replacement text.
    """

    def recursive_text_replace(branch: EtreeElement):
        """Replace any text element contining old with one or more elements.

        :param branch: an etree element
        """
        for elem in tuple(branch):
            if not elem.text or old not in elem.text:
                recursive_text_replace(elem)
                continue

            # create a new text element for each line in replacement text
            text = elem.text.replace(old, new)
            new_elems = [_copy_new_text(elem, line) for line in text.splitlines()]

            # insert breakpoints where line breaks were
            breaks = [_new_br_element(elem) for _ in new_elems]
            new_elems = [x for pair in zip(new_elems, breaks) for x in pair][:-1]

            # replace the original element with the new elements
            parent = elem.getparent()
            if parent is not None:
                index = parent.index(elem)
                parent[index : index + 1] = new_elems

    recursive_text_replace(root)


def replace_docx_text(
    path_in: str | os.PathLike[str],
    path_out: str | os.PathLike[str],
    *replacements: tuple[str, str],
    html: bool = False,
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
    reader.close()


def get_links(path_in: str | os.PathLike[str]) -> Iterator[tuple[str, str]]:
    """Yield links inside a docx file as (href, text).

    :param path_in: path to input docx
    :yield: every link in the file as a tuple of (href, text)
    :return: None
    """
    link_pattern = re.compile('<a href="(?P<href>[^"]+)">(?P<text>[^<]+)</a>')
    extraction = docx2python(path_in)
    for run in iter_at_depth(extraction.document_runs, 5):
        match = re.match(link_pattern, run)
        if match:
            href, text = match.groups()
            yield href, text
    extraction.close()


def get_headings(path_in: str | os.PathLike[str]) -> Iterator[list[str]]:
    """Yield paragraphs with 'Heading' patagraph_style.

    :param path_in: path to input docx
    :yield: every paragraph with 'Heading' paragraph_style as a list of strings
    :return: None

    When docx2python paragraph_styles parameter is set to True, the first run in
    every paragraph will be a paragraph style extracted from the xml, if present.
    Else, paragraphs style will be "".
    """
    heading_pattern = re.compile(r"Heading\d")
    with docx2python(path_in, html=True) as extraction:
        for par in iter_at_depth(extraction.document_pars, 4):
            if re.match(heading_pattern, par.style):
                yield par.run_strings
