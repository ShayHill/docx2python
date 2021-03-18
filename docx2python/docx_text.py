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
from itertools import groupby
from itertools import takewhile
import warnings
from contextlib import suppress
from typing import Any, Dict, List, Union, Iterator, Optional, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from .globs import DocxContext

from .attribute_register import KNOWN_ATTRIBUTES, KNOWN_TAGS, Tags
from . import numbering_formats as nums
from .depth_collector import DepthCollector
from .forms import get_checkBox_entry, get_ddList_entry
from .iterators import enum_at_depth
from .namespace import qn
from .text_runs import get_run_style, style_close, style_open, gather_Pr, get_style

TablesList = List[List[List[List[str]]]]

""" Property 'known_tags' to help filter xml for meaningful content. """


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


def get_text_child(elem: Element) -> Optional[Element]:
    """
    Consolidate any text element children in elem. Return <w:t> or None if none

    :param elem: any xml element
    :return: search one level down and return text element if found

    There may be a potential for multiple text elements. In that case, this alters
    the parent elem by consolidating all <w:t> children.
    """
    text_elements = [x for x in elem if x.tag == Tags.TEXT]
    if text_elements:
        text_elements[0].text = "".join(x.text for x in text_elements)
        for elem in text_elements[1:]:
            del elem
        return text_elements[0]


def elem_key(elem: Element) -> Tuple[str, Dict[str, str], List[Tuple[str, str]]]:
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


# TODO: delete is_equivalent
def is_equivalent(elem_a: Element, elem_b: Element) -> bool:
    """
    Elements are of the same type, attrib (excluding rsid keys), and Pr

    :param elem_a: any xml element
    :param elem_b: any xml element
    :return: are same type with same attrib (excluding rsid keys) and Pr

    rsid attributes mark revisions. These are not considered by docx2python.
    """
    if elem_a.tag != elem_b.tag:
        return False

    def attrib_without_rsid(elem: Element) -> Dict[str, str]:
        """
        Attrib dict of an element without 'rsid...' keys.

        :param elem: xml element
        :return: attributes that are not rsid (version markers)
        """
        return {
            k: v
            for k, v in elem.attrib.items()
            if not k.split("}")[-1].startswith("rsid")
        }

    if attrib_without_rsid(elem_a) != attrib_without_rsid(elem_b):
        return False

    return gather_Pr(elem_a) == gather_Pr(elem_b)


def _has_content(tree: Element) -> Optional[str]:
    """
    Does the element have any descendent content elements?

    :param tree: xml element
    :return: first content tag found or None if no content tags are found?

    This is to check for text in any skipped elements.

    Docx2Python ignores spell check, revision, and other elements. This function checks
    that no content (paragraphs, run, text, link, ...) is contained in children of any
    ignored elements.

    If no content is found, the element can be safely ignored.
    """

    def iter_known_tags(tree_: Element) -> Iterator[str]:
        """ Yield all known tags in tree """
        if tree_.tag in KNOWN_TAGS:
            yield tree_.tag
        for branch in tree_:
            yield from iter_known_tags(branch)

    return next(iter_known_tags(tree), None)


# TODO: factor out get_run_text
def get_run_text(branch: Element) -> Union[str, None]:
    """
    Find the text element in a run and return the text.

    # TODO: improve docstring for get_run_text
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


def _is_run(elem: Element) -> bool:
    return elem.tag == Tags.RUN


def merge_runs(tree: Element) -> None:
    # TODO: docstromg
    # TODO: make recursive
    elems = [x for x in tree if x.tag in KNOWN_TAGS]
    runs = [list(y) for x, y in groupby(elems, key=elem_key)]
    runs = [x for x in runs if len(x) > 1 and x[0].tag in {Tags.HYPERLINK}]

    for run in (x for x in runs if x[0].tag == Tags.RUN):
        text_elems = [get_text_child(x) for x in run]
        text_elems = [x for x in text_elems if x is not None]
        if text_elems:
            text_elems[0].text = "".join(x.text for x in text_elems)
            for elem in run[1:]:
                tree.remove(elem)


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
        merge_runs(branch)
        for child in branch:
            tag = child.tag
            if tag not in KNOWN_TAGS:
                content_tag = _has_content(child)
                if content_tag:
                    warnings.warn(
                        f"Ignoring tag {tag} with content in {content_tag}. "
                        f"Tag {tag} is not implemented in docx2python."
                    )

            # set caret depth
            if tag == Tags.TABLE:
                tables.set_caret(1)
            elif tag == Tags.TABLE_ROW:
                tables.set_caret(2)
            elif tag == Tags.TABLE_CELL:
                tables.set_caret(3)
            elif tag == Tags.PARAGRAPH:
                tables.set_caret(4)

            # open elements
            if tag == Tags.PARAGRAPH:
                tables.insert(_get_bullet_string(child, context))

            elif tag == Tags.RUN and do_html is True:
                # new text run
                run_style = get_run_style(child)
                open_style = getattr(tables, "open_style", ())
                if run_style != open_style:
                    tables.insert(style_close(open_style))
                    tables.insert(style_open(run_style))
                    tables.open_style = run_style

            elif tag == Tags.TEXT:
                # new text object. oddly enough, these don't all contain text
                text = child.text if child.text is not None else ""
                if do_html is True:
                    text = text.replace("<", "&lt;")
                    text = text.replace(">", "&gt;")
                tables.insert(text)

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

            # close elements
            if tag == Tags.PARAGRAPH and do_html is True:
                tables.insert(style_close(getattr(tables, "open_style", ())))
                tables.open_style = ()

            if tag in {Tags.TABLE_ROW, Tags.TABLE_CELL, Tags.PARAGRAPH}:
                tables.raise_caret()

            elif tag == Tags.TABLE:
                tables.set_caret(1)

            elif tag == Tags.HYPERLINK:
                tables.insert("</a>")

    root = ElementTree.fromstring(xml)
    branches(root)

    tree = tables.tree
    for (i, j, k, l), paragraph in enum_at_depth(tree, 4):
        tree[i][j][k][l] = "".join(paragraph)

    return tree
