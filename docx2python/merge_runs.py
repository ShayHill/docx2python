""" Merge runs with identical formatting.

:author: Shay Hill
:created: 12/13/2021

Join consecutive xml runs with identical formatting. See docstring for ``merge_elems``.
"""
from __future__ import annotations

import functools
from itertools import groupby
from typing import TYPE_CHECKING

from lxml.etree import _Element as EtreeElement  # type: ignore

from .attribute_register import RELS_ID, Tags, has_content
from .text_runs import get_html_formatting

if TYPE_CHECKING:
    from .docx_reader import File

# identify tags that will be merged together (if formatting is equivalent)
_MERGEABLE_TAGS = {Tags.RUN, Tags.HYPERLINK, Tags.TEXT, Tags.TEXT_MATH}


def _elem_key(file: File, elem: EtreeElement) -> tuple[str, str, list[str]]:
    """
    Enough information to tell if two elements are more-or-less identically formatted.

    :param elem: any element in an xml file.
    :return: A summary of attributes (if two adjacent elements return the same key,
        they are considered mergeable). Only used to merge elements, so returns None
        if element tags are not in _MERGEABLE_TAGS.

    Ignore text formatting differences if consecutive link elements point to the same
    address. Always join these.

    Docx2Text joins consecutive runs and links of the same style. Comparing two
    elem_key return values will tell you if
        * elements are the same type
        * link rels ids reference the same link
        * run styles are the same (as far as docx2python understands them)

    Elem rId attributes are replaced with rId['Target'] because different rIds can
    point to identical targets. This is important for hyperlinks, which can look
    different but point to the same address.

    """
    tag = elem.tag
    if tag not in _MERGEABLE_TAGS:
        return tag, "", []

    # always join links pointing to the same address
    rels_id = elem.attrib.get(RELS_ID)
    if rels_id:
        return tag, str(file.rels[str(rels_id)]), []

    return tag, "", get_html_formatting(elem, file.context.xml2html_format)


def merge_elems(file: File, tree: EtreeElement) -> None:
    """
    Recursively merge duplicate (as far as docx2python is concerned) elements.

    :param file: File instancce
    :param tree: root_element from an xml in File instance
    :effects: Merges consecutive elements if tag, attrib, and style are the same

    There are a few ways consecutive elements can be "identical":
        * same link
        * same style

    Often, consecutive, "identical" elements are written as separate elements,
    because they aren't identical to Word. Word keeps track of revision history,
    spelling errors, etc., which are meaningless to docx2python.

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hy</w:t>
            </w:r>
        </w:hyperlink>
        <w:proofErr/>  <!-- docx2python will ignore this proofErr -->
        <w:hyperlink r:id="rId8">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>per</w:t>
            </w:r>
        </w:hyperlink>
        <w:hyperlink r:id="rId9">  <!-- points to http://www.shayallenhill.com -->
            <w:r w:rsid="asdfas">  <!-- docx2python will ignore this rsid -->
                <w:t>link</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

    Docx2python condenses the above to (by merging links)

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hy</w:t>
            </w:r>
            <w:r>
                <w:t>per</w:t>
            </w:r>
            <w:r w:rsid="asdfas">  <!-- docx2python will ignore this rsid -->
                <w:t>link</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

    Then to (by merging runs)

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hy</w:t>
                <w:t>per</w:t>
                <w:t>link</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

    Then finally to (by merging text)

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hyperlink</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

    This function only merges runs, text, and hyperlinks, because merging paragraphs
    or larger elements would ignore information docx2python DOES want to preserve.

    Filter out non-content items so runs can be joined even
    """

    file_elem_key = functools.partial(_elem_key, file)

    elems = [x for x in tree if has_content(x)]
    runs = [list(y) for _, y in groupby(elems, key=file_elem_key)]

    for run in (x for x in runs if len(x) > 1 and x[0].tag in _MERGEABLE_TAGS):
        if run[0].tag in {Tags.TEXT, Tags.TEXT_MATH}:
            run[0].text = "".join(x.text or "" for x in run)
        for elem in run[1:]:
            for e in elem:
                run[0].append(e)
            tree.remove(elem)

    for branch in tree:
        merge_elems(file, branch)
