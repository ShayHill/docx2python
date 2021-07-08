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
from typing import Iterator, Optional

from lxml import etree

from docx2python.namespace import qn


@dataclass
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


KNOWN_ATTRIBUTES = {qn("r:id")}
