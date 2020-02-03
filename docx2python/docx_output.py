#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Output format for extracted docx content.

:author: Shay Hill
:created: 7/5/2019
"""
from typing import Any, Dict

from docx2python.docx_text import TablesList
from docx2python.iterators import get_html_map, iter_at_depth


class DocxContent:
    """Holds return values for docx content."""

    def __init__(
        self,
        *,
        header: TablesList,
        footer: TablesList,
        body: TablesList,
        footnotes: TablesList,
        endnotes: TablesList,
        properties: Dict[str, Any],
        images: Dict[str, bytes]
    ) -> None:
        self.header = header
        self.footer = footer
        self.body = body
        self.footnotes = footnotes
        self.endnotes = endnotes
        self.properties = properties
        self.images = images

    @property
    def document(self) -> TablesList:
        """All docx "tables" concatenated."""
        return self.header + self.body + self.footer + self.footnotes + self.endnotes

    @property
    def text(self) -> str:
        """All docx paragraphs, "\n\n" delimited."""
        return "\n\n".join(iter_at_depth(self.document, 4))

    @property
    def html_map(self) -> str:
        """A visual mapping of docx content."""
        return get_html_map(self.document)
