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

from docx2python.namespace import qn


@dataclass
class Tags:
    """
    These are the tags that provoke some action in docx2python.
    """

    TABLE: str = qn("w:tbl")
    TABLE_ROW: str = qn("w:tr")
    TABLE_CELL: str = qn("w:tc")
    PARAGRAPH: str = qn("w:p")
    RUN: str = qn("w:r")
    TEXT: str = qn("w:t")
    IMAGE: str = qn("a:blip")
    IMAGEDATA: str = qn("v:imagedata")
    TAB: str = qn("w:tab")
    FOOTNOTE_REFERENCE: str = qn("w:footnoteReference")
    ENDNOTE_REFERENCE: str = qn("w:endnoteReference")
    FOOTNOTE: str = qn("w:footnote")
    ENDNOTE: str = qn("w:endnote")
    HYPERLINK: str = qn("w:hyperlink")
    FORM_CHECKBOX: str = qn("w:checkBox")
    FORM_DDLIST: str = qn("w:ddList")  # drop-down form


KNOWN_TAGS = {x.default for x in Tags.__dataclass_fields__.values()}
KNOWN_ATTRIBUTES = {qn("r:id")}
