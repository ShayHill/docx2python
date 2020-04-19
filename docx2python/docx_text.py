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
import warnings
from typing import Any, Dict, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from docx2python import numbering_formats as nums
from docx2python.depth_collector import DepthCollector
from docx2python.iterators import enum_at_depth
from docx2python.namespace import qn
from docx2python.text_runs import get_run_style, style_close, style_open

TablesList = List[List[List[List[str]]]]

# frequent qn calls
TABLE = qn("w:tbl")
TABLE_ROW = qn("w:tr")
TABLE_CELL = qn("w:tc")
PARAGRAPH = qn("w:p")
RUN = qn("w:r")
TEXT = qn("w:t")
IMAGE = qn("a:blip")
IMAGEDATA = qn("v:imagedata")
TAB = qn("w:tab")
FOOTNOTE_REFERENCE = qn("w:footnoteReference")
ENDNOTE_REFERENCE = qn("w:endnoteReference")
FOOTNOTE = qn("w:footnote")
ENDNOTE = qn("w:endnote")
HYPERLINK = qn("w:hyperlink")


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
        numFmt = context["numId2numFmts"][numId][int(ilvl)]
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


def get_text(xml: bytes, context: Dict[str, Any]) -> TablesList:
    """Xml as a string to a list of cell strings.

    :param xml: an xml bytes object which might contain text
    :param context: dictionary of document attributes generated in get_docx_text
    :returns: A 4-deep nested list of strings.

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
        for child in branch:
            tag = child.tag

            # set caret depth
            if tag == TABLE:
                tables.set_caret(1)
            elif tag == TABLE_ROW:
                tables.set_caret(2)
            elif tag == TABLE_CELL:
                tables.set_caret(3)
            elif tag == PARAGRAPH:
                tables.set_caret(4)

            # open elements
            if tag == PARAGRAPH:
                tables.insert(_get_bullet_string(child, context))

            elif tag == RUN and do_html is True:
                # new text run
                run_style = get_run_style(child)
                open_style = getattr(tables, "open_style", ())
                if run_style != open_style:
                    tables.insert(style_close(open_style))
                    tables.insert(style_open(run_style))
                    tables.open_style = run_style

            elif tag == TEXT:
                # new text object. oddly enough, these don't all contain text
                text = child.text if child.text is not None else ""
                if do_html is True:
                    text = text.replace("<", "&lt;")
                    text = text.replace(">", "&gt;")
                tables.insert(text)

            elif tag == FOOTNOTE:
                if "separator" not in child.attrib.get(qn("w:type"), "").lower():
                    tables.insert("footnote{})\t".format(child.attrib[qn('w:id')]))

            elif tag == ENDNOTE:
                if "separator" not in child.attrib.get(qn("w:type"), "").lower():
                    tables.insert("endnote{})\t".format(child.attrib[qn('w:id')]))

            elif tag == HYPERLINK:
                rId = child.attrib[qn("r:id")]
                link = context["rId2Target"].get(rId)
                if link:
                    tables.insert("<a href=\"{}\">".format(link))

            # add placeholders
            elif tag == FOOTNOTE_REFERENCE:
                tables.insert("----footnote{}----".format(child.attrib[qn('w:id')]))

            elif tag == ENDNOTE_REFERENCE:
                tables.insert("----endnote{}----".format(child.attrib[qn('w:id')]))

            elif tag == IMAGE:
                rId = child.attrib[qn("r:embed")]
                image = context["rId2Target"].get(rId)
                if image:
                    tables.insert("----{}----".format(image))

            elif tag == IMAGEDATA:
                rId = child.attrib[qn("r:id")]
                image = context["rId2Target"].get(rId)
                if image:
                    tables.insert("----{}----".format(image))

            elif tag == TAB:
                tables.insert("\t")

            # enter child element
            branches(child)

            # close elements
            if tag == PARAGRAPH and do_html is True:
                tables.insert(style_close(getattr(tables, "open_style", ())))
                tables.open_style = ()

            if tag in {TABLE_ROW, TABLE_CELL, PARAGRAPH}:
                tables.raise_caret()

            elif tag == TABLE:
                tables.set_caret(1)

            elif tag == HYPERLINK:
                tables.insert('</a>')

    branches(ElementTree.fromstring(xml))

    tree = tables.tree
    for (i, j, k, l), paragraph in enum_at_depth(tree, 4):
        tree[i][j][k][l] = "".join(paragraph)

    return tree
