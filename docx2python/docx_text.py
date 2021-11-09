#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Extract text from docx content files.

:author: Shay Hill
:created: 6/6/2019

Content in the extracted docx is found in the ``word`` folder:
    ``word/document.html``
    ``word/header1.html``
    ``word/footer1.html``
"""
from __future__ import annotations

import functools
import warnings
from collections import defaultdict
from contextlib import suppress
from itertools import groupby
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, Set

from lxml import etree

from . import numbering_formats as nums
from .attribute_register import RELS_ID, Tags, has_content
from .depth_collector import DepthCollector
from .forms import get_checkBox_entry, get_ddList_entry
from .namespace import qn
from .text_runs import (
    _format_Pr_into_html,
    get_pStyle,
    get_run_formatting,
    get_html_formatting,
    get_paragraph_formatting,
    _gather_Pr,
    _elem_tag_str,
    html_open,
    html_close,
)

TablesList = List[List[List[List[str]]]]


def _new_list_counter() -> defaultdict[Any, defaultdict[Any, 0]]:
    """
    A counter, starting at zero, for each numId

    :return: {
        a_numId: 0,
        b_numId: 0
    }

    This is what you need to keep track of where every nested list is at.
    """
    return defaultdict(lambda: defaultdict(lambda: 0))


def _increment_list_counter(ilvl2count: Dict[str, int], ilvl: str) -> int:
    # noinspection SpellCheckingInspection
    """
    Increase counter at ilvl, reset counter at deeper levels.

    :param ilvl2count: context['numId2count']
    :param ilvl: string representing an integer
    :return: updated count at ilvl.
        updates context['numId2count'] by reference

    On a numbered list, the count for sub-lists should reset when a parent list
    increases, e.g.,

    1. top-level list
        a. sublist
        b. sublist continues
    2. back to top-level list
        a. sublist counter has been reset

    List counters are defaultdicts, so we can reset sublist counters by deleting them.
    """
    ilvl2count[ilvl] += 1
    deeper_levels = [x for x in ilvl2count.keys() if x > ilvl]
    for level in deeper_levels:
        del ilvl2count[level]
    return ilvl2count[ilvl]


# noinspection PyPep8Naming
def _get_bullet_string(
    numId2numFmts: Dict[str, List[str]],
    numId2count: defaultdict[Any, defaultdict[Any, 0]],
    paragraph: etree.Element,
) -> str:
    """
    Get bullet string if paragraph is numbered. (e.g, '--  ' or '1)  ')

    :param paragraph: <w:p> xml element
    :return: specified 'bullet' string or '' if paragraph is not numbered

    <w:p>
        <w:pPr>
            <w:numPr>
                <w:ilvl w:val="0"/>
                <w:numId w:val="9"/>
            </w:numPr>
        </wpPr>
        <w:r>
            <w:t>this text in numbered or bulleted list
            </w:t>
        </w:r>
    </w:p>

    bullet preceded by four spaces for every indentation level.
    """
    try:
        pPr = paragraph.find(qn("w:pPr"))
        numPr = pPr.find(qn("w:numPr"))
        numId = numPr.find(qn("w:numId")).attrib[qn("w:val")]
        ilvl = numPr.find(qn("w:ilvl")).attrib[qn("w:val")]
        try:
            numFmt = numId2numFmts[numId][int(ilvl)]
        except IndexError:
            # give up and put a bullet
            numFmt = "bullet"
    except (AttributeError, KeyError):
        # not a numbered paragraph
        return ""

    number = _increment_list_counter(numId2count[numId], ilvl)
    indent = "\t" * int(ilvl)

    def format_bullet(bullet: str) -> str:
        """Indent, format and pad the bullet or number string."""
        if bullet != nums.bullet():
            bullet += ")"
        return indent + bullet + "\t"

    if numFmt == "decimal":
        return format_bullet(nums.decimal(number))
    elif numFmt == "lowerLetter":
        return format_bullet(nums.lower_letter(number))
    elif numFmt == "upperLetter":
        return format_bullet(nums.upper_letter(number))
    elif numFmt == "lowerRoman":
        return format_bullet(nums.lower_roman(number))
    elif numFmt == "upperRoman":
        return format_bullet(nums.upper_roman(number))
    elif numFmt == "bullet":
        return format_bullet(nums.bullet())
    else:
        warnings.warn(
            "{} numbering format not implemented, substituting '{}'".format(
                numFmt, nums.bullet()
            )
        )
        return format_bullet(nums.bullet())


_MERGEABLE_TAGS = {Tags.RUN, Tags.HYPERLINK, Tags.TEXT, Tags.TEXT_MATH}


def _elem_key(
    file: File, elem: etree.Element, ignore_formatting: bool = False
) -> Tuple[str, str, List[str]]:
    # noinspection SpellCheckingInspection
    """
    Enough information to tell if two elements are more-or-less identically formatted.

    :param elem: any element in an xml file.
    :return: A summary of attributes (if two adjacent elements return the same key,
        they are considered mergeable). Only used to merge elements, so returns None if
        element tags are not in _MERGEABLE_TAGS.

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
        return tag, file.rels[rels_id], []

    # TODO: see if ignore_formatting is ever used
    if ignore_formatting:
        return tag, "", []

    return tag, "", get_html_formatting(elem, file.context.xml2html_format)


def merge_elems(file: File, tree: etree.Element) -> None:
    # noinspection SpellCheckingInspection
    """
    Recursively merge duplicate (as far as docx2python is concerned) elements.

    :param file: File instancce
    :param tree: root_element from an xml in File instance
    :return: None
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
    runs = [list(y) for x, y in groupby(elems, key=file_elem_key)]

    for run in (x for x in runs if len(x) > 1 and x[0].tag in _MERGEABLE_TAGS):
        if run[0].tag in {Tags.TEXT, Tags.TEXT_MATH}:
            run[0].text = "".join(x.text for x in run)
        for elem in run[1:]:
            run[0].extend(elem)
            tree.remove(elem)

    for branch in tree:
        merge_elems(file, branch)


def _get_elem_depth(tree: etree.Element) -> Optional[int]:
    """
    What depth is this element in a nested list, relative to paragraphs (depth 4)?

    :param tree: element in a docx content xml (header, footer, officeDocument, etc.)

    :return: 4 - recursion depth;
        None if no paragraphs are found or if descending into nest would cause a
        false start (e.g., Tags.DOCUMENT or Tags.BODY which often have A paragraph (but
        not the next paragraph) at one or two levels down.

    Typically, the docx is a table of tables::

        [  # entire document
            [  # table
                [  # table row
                    [  # table cell
                        [  # paragraph
                            "",  # run
                            "",  # run
                            "",  # run
                        ]
                    ]
                ]
            ]
        ]

    But this isn't always the case. Instead of looking explicitly for tables,
    table rows, and table cells, look inside elements for paragraphs to determine
    depth in the nested list.

    E.g., given a table row element with a paragraph two levels in, return 2.
    So, depth of element will be 4 - 2 = 3.

    document = depth 0
    table = depth 1
    table row = depth 2
    table cell = depth 3
    paragraph = depth 4
    below paragraph = depth 5

    There will only ever be one document list, so the min depth returned is 1
    """

    if tree.tag in {Tags.DOCUMENT, Tags.BODY}:
        return

    def search_at_depth(tree_: Sequence[etree.Element], _depth=0):
        """ Width-first recursive search for Tags.PARAGRAPH """
        if not tree_:
            return
        if any(x.tag == Tags.PARAGRAPH for x in tree_):
            return max(4 - _depth, 1)
        return search_at_depth(sum([list(x) for x in tree_], start=[]), _depth + 1)

    return search_at_depth([tree])


# noinspection PyPep8Naming
def get_text(file: File, root: Optional[etree.Element] = None) -> TablesList:
    """
    Xml as a string to a list of cell strings.

    :param file: File instance from which text will be extracted.
    :param root: Optionally extract content from a single element.
        If None, root_element of file will be used.
    :returns: A 5-deep nested list of strings.

    Sorts the text into the DepthCollector instance, five-levels deep

    ``[table][row][cell][paragraph][run]`` is a string

    Joins the runs before returning, so return list will be

    ``[table][row][cell][paragraph]`` is a string

    If you'd like to extend or edit this package, this function is probably where you
    want to do it. Nothing tricky here except keeping track of the text formatting.
    """
    root = root if root is not None else file.root_element
    numId2count = _new_list_counter()
    tables = DepthCollector(5)

    xml2html = file.context.xml2html_format

    # noinspection PyPep8Naming
    def branches(tree: etree.Element) -> None:
        """
        Recursively iterate over tree. Add text when found.

        :param tree: An Element from an xml file (etree)
        :return: None. Adds text cells to outer variable `tables`.
        """

        # queue up tags before opening any paragraphs or runs
        if tree.tag == Tags.PARAGRAPH:
            if file.context.do_pStyle:
                tables.add_pStyle(get_pStyle(tree))
            tables.add_pPs(get_paragraph_formatting(tree, xml2html))

        elif tree.tag == Tags.RUN:
            tables.add_rPs(get_run_formatting(tree, xml2html))

        # set appropriate depth for element (this will trigger methods in ``tables``)
        tree_depth = _get_elem_depth(tree)
        tables.set_caret(tree_depth)

        # add text where found
        if tree.tag == Tags.PARAGRAPH:
            tables.insert(
                _get_bullet_string(file.context.numId2numFmts, numId2count, tree)
            )

        elif tree.tag in {Tags.TEXT, Tags.TEXT_MATH}:
            # oddly enough, these don't all contain text
            text = tree.text if tree.text is not None else ""
            if xml2html:
                text = text.replace("<", "&lt;")
                text = text.replace(">", "&gt;")
            tables.insert_text(text)

        elif tree.tag == Tags.BR:
            tables.insert_text("\n")

        elif tree.tag == Tags.SYM:
            font = tree.attrib.get(qn("w:font"))
            char = tree.attrib.get(qn("w:char"))
            if char:
                tables.insert_text("<span style=font-family:{}>&#x0{};</span>".format(font, char[1:]))

        elif tree.tag == Tags.FOOTNOTE:
            if "separator" not in tree.attrib.get(qn("w:type"), "").lower():
                tables.queue_paragraph_text(
                    "footnote{})\t".format(tree.attrib[qn("w:id")])
                )

        elif tree.tag == Tags.ENDNOTE:
            if "separator" not in tree.attrib.get(qn("w:type"), "").lower():
                tables.queue_paragraph_text(
                    "endnote{})\t".format(tree.attrib[qn("w:id")])
                )

        elif tree.tag == Tags.HYPERLINK:
            # look for an href, ignore internal references (anchors)
            with suppress(KeyError):
                rId = tree.attrib[qn("r:id")]
                link = file.rels[rId]
                tables.queue_rPr(['a href="{}"'.format(link)])

        if tree.tag == Tags.FORM_CHECKBOX:
            tables.insert(get_checkBox_entry(tree))

        elif tree.tag == Tags.FORM_DDLIST:
            tables.insert(get_ddList_entry(tree))

        elif tree.tag == Tags.FOOTNOTE_REFERENCE:
            tables.insert("----footnote{}----".format(tree.attrib[qn("w:id")]))

        elif tree.tag == Tags.ENDNOTE_REFERENCE:
            tables.insert("----endnote{}----".format(tree.attrib[qn("w:id")]))

        elif tree.tag == Tags.IMAGE:
            with suppress(KeyError):
                rId = tree.attrib[qn("r:embed")]
                image = file.rels[rId]
                tables.insert("----{}----".format(image))

        elif tree.tag == Tags.IMAGEDATA:
            with suppress(KeyError):
                rId = tree.attrib[qn("r:id")]
                image = file.rels[rId]
                tables.insert("----{}----".format(image))

        elif tree.tag == Tags.TAB:
            tables.insert("\t")

        for branch in tree:
            branches(branch)

        tables.set_caret(tree_depth)

    branches(root)

    return tables.tree
