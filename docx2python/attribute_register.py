#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" The tags and attributes docx2python knows how to handle.

:author: Shay Hill
:created: 3/18/2021

A lot of the information in a docx file isn't text or text attributes. Docx files
record spelling errors, revision history, etc. Docx2Python will ignore (by design)
much of this.
"""
from dataclasses import dataclass
from typing import Callable, Iterator, NamedTuple, Optional

from lxml import etree

from docx2python.namespace import qn


# TODO: document extension of HtmlFormatter
class HtmlFormatter(NamedTuple):
    formatter: Callable[[str, str], str] = lambda tag, val: tag
    container: Optional[str] = None  # e.g., 'span'
    property: Optional[str] = None  # e.g., 'font-size'


xml2html_formatter = {
    "b": HtmlFormatter(),
    "i": HtmlFormatter(),
    "u": HtmlFormatter(),
    "strike": HtmlFormatter(lambda tag, val: "s"),
    "vertAlign": HtmlFormatter(lambda tag, val: val[:3]),  # subscript and superscript
    "smallCaps": HtmlFormatter(
        lambda tag, val: "font-variant:small-caps", "span", "style"
    ),
    "caps": HtmlFormatter(lambda tag, val: "text-transform:uppercase", "span", "style"),
    "highlight": HtmlFormatter(
        lambda tag, val: f"background-color:{val}", "span", "style"
    ),
    "sz": HtmlFormatter(lambda tag, val: f"font-size:{val}pt", "span", "style"),
    "color": HtmlFormatter(lambda tag, val: f"color:{val}", "span", "style"),
    "Heading1": HtmlFormatter(lambda tag, val: "h1"),
    "Heading2": HtmlFormatter(lambda tag, val: "h2"),
    "Heading3": HtmlFormatter(lambda tag, val: "h3"),
    "Heading4": HtmlFormatter(lambda tag, val: "h4"),
    "Heading5": HtmlFormatter(lambda tag, val: "h5"),
    "Heading6": HtmlFormatter(lambda tag, val: "h6"),
}


@dataclass(frozen=True)
class Tags:
    """
    These are the tags that provoke some action in docx2python.
    """

    BODY: str = qn("w:body")
    BR: str = qn("w:br")
    DOCUMENT: str = qn("w:document")
    ENDNOTE: str = qn("w:endnote")
    ENDNOTE_REFERENCE: str = qn("w:endnoteReference")
    FOOTNOTE: str = qn("w:footnote")
    FOOTNOTE_REFERENCE: str = qn("w:footnoteReference")
    FORM_CHECKBOX: str = qn("w:checkBox")
    FORM_DDLIST: str = qn("w:ddList")  # drop-down form
    HYPERLINK: str = qn("w:hyperlink")
    IMAGE: str = qn("a:blip")
    IMAGEDATA: str = qn("v:imagedata")
    PARAGRAPH: str = qn("w:p")
    PAR_PROPERTIES: str = qn("w:pPr")
    RUN: str = qn("w:r")
    RUN_PROPERTIES: str = qn("w:rPr")
    TAB: str = qn("w:tab")
    TABLE: str = qn("w:tbl")
    TABLE_CELL: str = qn("w:tc")
    TABLE_ROW: str = qn("w:tr")
    TEXT: str = qn("w:t")
    TEXT_MATH: str = qn("m:t")


KNOWN_TAGS = {x.default for x in Tags.__dataclass_fields__.values()}


def has_content(tree: etree.Element) -> Optional[str]:
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
    content_tags = KNOWN_TAGS - {Tags.RUN_PROPERTIES, Tags.PAR_PROPERTIES}
    if tree.tag in content_tags:
        return tree.tag

    def iter_known_tags(tree_: etree.Element) -> Iterator[str]:
        """ Yield all known tags in tree """
        if tree_.tag in content_tags:
            yield tree_.tag
        for branch in tree_:
            yield from iter_known_tags(branch)

    return next(iter_known_tags(tree), None)


# known attributes are compared to determine if runs are distinct (if runs are not
# distinguishable by docx2text--e.g., runs that only differ by revision--they will be
# joined). For this purpose, rSid (revision id) is considered an "unknown attribute".
KNOWN_ATTRIBUTES = {qn("r:id")}
