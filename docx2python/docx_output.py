#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Output format for extracted docx content.

:author: Shay Hill
:created: 7/5/2019

Holds runs in a 5-deep nested list (paragraphs are lists of text runs [strings])::

    [  # tables
        [  # table
            [  # row
                [  # cell
                    [  # paragraph
                        "run 1 ",  # text run
                        "run 2 ",  # text run
                        "run 3"  # text run
                    ]
                ]
            ]
        ]
    ]

_runs properties (e.g., ``header_runs``) return text in this format.

Also returns a 4-deep nested list (paragraphs are strings)::

    [  # tables
        [  # table
            [  # row
                [  # cell
                    "run 1 run 2 run 3"  # paragraph
                ]
            ]
        ]
    ]

This is the format for default (no trailing "_runs", e.g ``header``) properties.

"""
from typing import Dict, List, Any

from .attribute_dicts import filter_files_by_type, get_path
from .docx_context import collect_docProps
from .docx_text import TablesList
from .iterators import enum_at_depth
from .iterators import get_html_map, iter_at_depth
import zipfile
from warnings import warn
from copy import deepcopy

from .globs import DocxContext


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
        zipf: zipfile.ZipFile,
        context: DocxContext
    ) -> None:
        self.header_runs = header
        self.footer_runs = footer
        self.body_runs = body
        self.footnotes_runs = footnotes
        self.endnotes_runs = endnotes
        self.images = images
        self.files = files
        self.zipf = zipf
        self.context = context

    def __getattr__(self, item) -> Any:
        """
        Create depth-four paragraph tables form depth-five run tables.

        :param item:
        :return:

        Docx2Python v1 joined runs into paragraphs earlier in the code. Docx2Python v2
        exposes runs to the user, but still returns paragraphs by default.
        """
        if item in {"header", "footer", "body", "footnotes", "endnotes"}:
            runs = deepcopy(getattr(self, item + "_runs"))
            for (i, j, k, l), paragraph in enum_at_depth(runs, 4):
                runs[i][j][k][l] = "".join(paragraph)
            return runs
        raise AttributeError()

    @property
    def document(self) -> TablesList:
        """All docx "tables" concatenated."""
        return self.header + self.body + self.footer + self.footnotes + self.endnotes

    @property
    def document_runs(self) -> TablesList:
        """All docx x_runs properties concatenated."""
        return (
            self.header_runs
            + self.body_runs
            + self.footer_runs
            + self.footnotes_runs
            + self.endnotes_runs
        )

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
