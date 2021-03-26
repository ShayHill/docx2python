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
from copy import deepcopy
import warnings
from contextlib import suppress
from itertools import groupby
from typing import Any, Dict, List, Tuple, Union, Sequence, Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from . import numbering_formats as nums
from .attribute_register import KNOWN_ATTRIBUTES, Tags, has_content
from .depth_collector import DepthCollector
from .forms import get_checkBox_entry, get_ddList_entry
from .globs import DocxContext
from .iterators import enum_at_depth
from .iterators import get_text as gett_text
from .namespace import qn
from .text_runs import (
    get_pStyle,
    _elem_tag_str,
    get_run_style,
    get_style,
    style_close,
    style_open,
    get_Pr_as_html_strings,
    format_Pr,
    gather_Pr,
)

# TODO: rename iterators.get_text

TablesList = List[List[List[List[str]]]]


def _increment_list_counter(ilvl2count: Dict[str, int], ilvl: str) -> int:
    """
    Increase counter at ilvl, reset counter at deeper levels.

    :param ilvl2count: context['numId2count']
    :param ilvl: string representing an integer
    :return: updated count at ilvl.
        updates context['numId2count'] by reference

    On a numbered list, the count for sublists should reset when a parent list
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
def _get_bullet_string(paragraph: ElementTree.Element, context: Dict[str, Any]) -> str:
    """
    Get bullet string if paragraph is numbered. (e.g, '--  ' or '1)  ')

    :param paragraph: <w:p> xml element
    :param context: dictionary of document attributes generated in ``get_context``
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
            numFmt = context["numId2numFmts"][numId][int(ilvl)]
        except IndexError:
            # give up and put a bullet
            numFmt = "bullet"
    except (AttributeError, KeyError):
        # not a numbered paragraph
        return ""

    number = _increment_list_counter(context["numId2count"][numId], ilvl)
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


def _elem_key(elem: Element) -> Tuple[str, Dict[str, str], List[Tuple[str, str]]]:
    """
    Enough information to tell if two elements are more-or-less identical.

    :param elem:
    :return:

    Docx2Text joins consecutive runs and links of the same style. Comparing two
    elem_key return values will tell you if
        * elements are the same type
        * element attributes are same excluding revision 'rsid'
        * element styles are the (as far as docx2python understands them)

    Elem rId attributes are replaces with rId['Target'] because different rIds can
    point to identical targets. This is important for hyperlinks, which can look
    different but point to the same address.
    """
    tag = elem.tag
    attrib = {k: v for k, v in elem.attrib.items() if k in KNOWN_ATTRIBUTES}
    for k, v in attrib.items():
        with suppress(KeyError):
            attrib[k] = DocxContext.current_file_rels[v]["Target"]
    style = get_style(elem)
    return tag, attrib, style


# TODO: factor out get_run_text (keep it around just a while for debugging)
def get_run_text(branch: Element) -> Union[str, None]:
    """
    Find the text element in a run and return the text.

    :param elem:
    :return:
    """

    def yield_text(branch_):
        for child in branch_:
            tag = child.tag
            if tag == Tags.TEXT:
                yield child.text
            yield from yield_text(child)
        yield ""

    return "".join(yield_text(branch))


def _merge_elems(tree: Element) -> None:
    """
    Recursively merge duplicate (as far as docx2python is concerned) elements.

    :param tree: element from an xml file
    :return: None
    :effects: Merges consecutive elements if tag, attrib, and style are the same

    There are a few ways consecutive elements can be "identical":
        * same link
        * same style

    Often, consecutive, "identical" elements are written as separate elements,
    because they aren't identical to Word. Work keeps track of revision history,
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

    This function only merges runs, text, and hyperlinks, because merging (e.g.)
    paragraphs would ignore information docx2python DOES want to preserve.
    """
    merge_tags = {Tags.RUN, Tags.HYPERLINK, Tags.TEXT}
    elems = [x for x in tree if has_content(x)]
    runs = [list(y) for x, y in groupby(elems, key=_elem_key)]

    for run in (x for x in runs if len(x) > 1 and x[0].tag in merge_tags):
        if run[0].tag == Tags.TEXT:
            run[0].text = "".join(x.text for x in run)
        for elem in run[1:]:
            run[0].extend(elem)
            tree.remove(elem)

    for branch in tree:
        _merge_elems(branch)


def _get_elem_depth(tree: Element) -> Optional[int]:
    """
    What depth is this element in a nested list, relative to paragraphs (depth 4)?

    :param tree: element in a docx content xml (header, footer, officeDocument, etc.)
    :param depth: internal use (tracks recursion depth)
    :return: 4 - recursion depth

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

    def search_at_depth(elems: Sequence[ElementTree.Element], _depth=0):
        """ Width-first recursive search for Tags.PARAGRAPH """
        if not elems:
            return
        if any(x.tag == Tags.PARAGRAPH for x in elems):
            return max(4 - _depth, 1)
        return search_at_depth(sum([list(x) for x in elems], start=[]), _depth + 1)

    return search_at_depth([tree])


def get_text(xml: bytes, context: Dict[str, Any], file_dict=None) -> TablesList:
    """Xml as a string to a list of cell strings.

    :param xml: an xml bytes object which might contain text
    :param context: dictionary of document attributes generated in get_docx_text
    :returns: A 5-deep nested list of strings.

    Sorts the text into the DepthCollector instance, five-levels deep

    ``[table][row][cell][paragraph][run]`` is a string

    Joins the runs before returning, so return list will be

    ``[table][row][cell][paragraph]`` is a string

    If you'd like to extend or edit this package, this function is probably where you
    want to do it. Nothing tricky here except keeping track of the text formatting.
    """
    tables = DepthCollector(5)
    do_html = context["do_html"]

    # noinspection PyPep8Naming
    def branches(branch: Element) -> None:
        """
        Recursively iterate over descendents of branch. Add text when found.

        :param branch: An Element from an xml file (ElementTree)
        :return: None. Adds text cells to outer variable `tables`.
        """

        if branch.tag == Tags.PARAGRAPH:
            if context["do_paragraph_styles"]:
                tables.add_pStyle(get_pStyle(branch))
            if context["do_html"]:
                tables.add_par_style(format_Pr({get_pStyle(branch): None}))

        tree_depth = _get_elem_depth(branch)
        tables.set_caret(tree_depth, reason="ts_" + branch.tag.split("}")[-1])
        # TODO: implement run_queue for footnotes, endnotes, etc.

        if branch.tag == Tags.PARAGRAPH:
            tables.insert(_get_bullet_string(branch, context))

        for child in branch:
            tag = child.tag

            if tag == Tags.RUN_PROPERTIES and do_html:
                tables._rPss = get_Pr_as_html_strings(child)

            # elif tag == Tags.PAR_PROPERTIES and do_html:
            #     par_style = {
            #         _elem_tag_str(x): x.attrib.get(qn("w:val")) for x in child
            #     }.get("pStyle", "")
            #     tables.run_queue = par_style + tables.run_queue

            elif tag == Tags.TEXT:
                # new text object. oddly enough, these don't all contain text
                text = child.text if child.text is not None else ""
                if do_html is True:
                    text = text.replace("<", "&lt;")
                    text = text.replace(">", "&gt;")
                tables.insert(text)

                # if "Table" in text:
                #     breakpoint()

            elif tag == Tags.FOOTNOTE:
                if "separator" not in child.attrib.get(qn("w:type"), "").lower():
                    tables.insert("footnote{})\t".format(child.attrib[qn("w:id")]))

            elif tag == Tags.ENDNOTE:
                if "separator" not in child.attrib.get(qn("w:type"), "").lower():
                    tables.insert("endnote{})\t".format(child.attrib[qn("w:id")]))

            elif tag == Tags.HYPERLINK:
                # look for an href, ignore internal references (anchors)
                with suppress(KeyError):
                    rId = child.attrib[qn("r:id")]
                    link = context["rId2Target"][rId]
                    tables.insert('<a href="{}">'.format(link))
                    close_elem = "</a>"

            elif tag == Tags.FORM_CHECKBOX:
                tables.insert(get_checkBox_entry(child))

            elif tag == Tags.FORM_DDLIST:
                tables.insert(get_ddList_entry(child))

            # add placeholders
            elif tag == Tags.FOOTNOTE_REFERENCE:
                tables.insert("----footnote{}----".format(child.attrib[qn("w:id")]))

            elif tag == Tags.ENDNOTE_REFERENCE:
                tables.insert("----endnote{}----".format(child.attrib[qn("w:id")]))

            elif tag == Tags.IMAGE:
                with suppress(KeyError):
                    rId = child.attrib[qn("r:embed")]
                    image = context["rId2Target"][rId]
                    tables.insert("----{}----".format(image))

            elif tag == Tags.IMAGEDATA:
                with suppress(KeyError):
                    rId = child.attrib[qn("r:id")]
                    image = context["rId2Target"][rId]
                    tables.insert("----{}----".format(image))

            elif tag == Tags.TAB:
                tables.insert("\t")

            # enter child element
            branches(child)

            # if tag == Tags.PARAGRAPH and do_html:
            #     tables.del_par_style()

            with suppress(UnboundLocalError):
                tables.insert(close_elem)

        # if branch.tag == Tags.PARAGRAPH:
        #     tables.close_paragraph()

        this_depth = tables.caret_depth
        ccc = deepcopy(tables.rightmost_branches)

        next_depth = tables.caret_depth

        # TODO: factor out caret reasons
        tables.set_caret(
            tree_depth,
            reset=False,
            reason="bs_" + branch.tag.split("}")[-1],
        )

        if branch.tag == Tags.TABLE:
            assert tables.caret_depth == 1
            # breakpoint()
            ccc = tables.rightmost_branches
            # breakpoint()
        if branch.tag == Tags.TABLE_ROW:
            assert tables.caret_depth == 2
            bbb = tables.rightmost_branches[-1]
            # breakpoint()
        if branch.tag == Tags.TABLE_CELL:
            assert tables.caret_depth == 3
            aaa = tables.rightmost_branches
            # breakpoint()
        if branch.tag == Tags.PARAGRAPH:
            assert tables.caret_depth == 4
            aaa = tables.rightmost_branches
            # breakpoint()

    root = ElementTree.fromstring(xml)
    _merge_elems(root)
    branches(root)

    tree = tables.tree

    # for (i, j, k, l), paragraph in enum_at_depth(tree, 4):
    #     tree[i][j][k][l] = "".join(paragraph)

    return tree
