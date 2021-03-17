#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Output format for extracted docx content.

:author: Shay Hill
:created: 7/5/2019
"""
from typing import Dict, List

from .attribute_dicts import filter_files_by_type, get_path
from .docx_context import collect_docProps
from .docx_text import TablesList
from .iterators import get_html_map, iter_at_depth
import zipfile
from warnings import warn


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
        images: Dict[str, bytes],
        files: List[Dict[str, str]],
        zipf: zipfile.ZipFile
    ) -> None:
        self.header = header
        self.footer = footer
        self.body = body
        self.footnotes = footnotes
        self.endnotes = endnotes
        self.images = images
        self.files = files
        self.zipf = zipf

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

    @property
    def properties(self) -> Dict[str, str]:
        """Document core-properties as a dictionary.

        Docx files created with Google docs won't have core-properties. If the file
        `core-properties` is missing, return an empty dict."""
        warn(
            "DocxContent.properties is deprecated and will be removed in some future "
            "version. Use DocxContent.core_properties.",
            FutureWarning,
        )
        return self.core_properties

    @property
    def core_properties(self) -> Dict[str, str]:
        """Document core-properties as a dictionary.

        Docx files created with Google docs won't have core-properties. If the file
        `core-properties` is missing, return an empty dict."""
        # TODO: test for a successful call of core-properties
        try:
            docProps = next(filter_files_by_type(self.files, "core-properties"))
            return collect_docProps(self.zipf.read(get_path(docProps)))
        except StopIteration:
            warn(
                "Could not find core-properties file (should be in docProps/core.xml) "
                "in DOCX, so returning an empty core_properties dictionary. Docx files "
                "created in Google Docs do not have a core-properties file, so this "
                "may be expected."
            )
            return {}
