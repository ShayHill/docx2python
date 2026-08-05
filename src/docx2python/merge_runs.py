"""Merge runs with identical formatting.

:author: Shay Hill
:created: 12/13/2021

Join consecutive xml runs with identical formatting. See docstring for ``merge_elems``.
"""

from __future__ import annotations

import functools
from itertools import groupby
from typing import TYPE_CHECKING

from docx2python.attribute_register import Tags, get_prefixed_tag, has_content
from docx2python.text_runs import get_html_formatting

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from docx2python.docx_reader import File

# identify tags that will be merged together (if formatting is equivalent)
_MERGEABLE_TAGS = {Tags.RUN, Tags.HYPERLINK, Tags.TEXT, Tags.TEXT_MATH}


def _is_mergeable(elem: EtreeElement) -> bool:
    """Can a run be merged with another run?"""
    return elem.tag in _MERGEABLE_TAGS or get_prefixed_tag(elem) in _MERGEABLE_TAGS


def _elem_key(file: File, elem: EtreeElement) -> tuple[str, str, list[str]]:
    """Return enough info to tell if two elements are closely formatted.

    :param elem: any element in an xml file.
    :return: A summary of attributes (if two adjacent elements return the same key,
        they are considered mergeable). Only used to merge elements, so returns None
        if elements are not mergeable.

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
    tag = str(elem.tag)
    if not _is_mergeable(elem):
        return tag, "", []

    # always join links pointing to the same address
    # elem.attrib key for relationship ids. These can find the information they
    # reference by ``file_instance.rels[elem.attrib[RELS_ID]]``
    rels_id_key = f"{{{elem.nsmap['r']}}}id"
    rels_id = elem.attrib.get(rels_id_key)
    if rels_id:
        return tag, str(file.rels[str(rels_id)]), []

    return tag, "", get_html_formatting(elem, file.context.xml2html_format)


def _is_text_or_text_math(elem: EtreeElement) -> bool:
    """Can an element be treated as text?"""
    text_or_text_math = {Tags.TEXT, Tags.TEXT_MATH}
    return elem.tag in text_or_text_math or get_prefixed_tag(elem) in text_or_text_math


def merge_elems(file: File, tree: EtreeElement) -> None:
    """Recursively merge duplicate (as far as docx2python is concerned) elements.

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

    for run in (x for x in runs if len(x) > 1 and _is_mergeable(x[0])):
        if _is_text_or_text_math(run[0]):
            run[0].text = "".join(x.text or "" for x in run)
        for elem in run[1:]:
            for e in elem:
                run[0].append(e)
            tree.remove(elem)

    for branch in tree:
        merge_elems(file, branch)
