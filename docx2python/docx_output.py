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
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict
from warnings import warn

from .docx_context import collect_docProps, pull_image_files
from .decode_docx import DocxReader
from .docx_text import TablesList
from .iterators import enum_at_depth, get_html_map, iter_at_depth


@dataclass
class DocxContent:
    """Holds return values for docx content."""

    context: DocxReader
    docx2python_kwargs: Dict[str, Any]

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
        raise AttributeError(f"no attribute {item}")

    def _get_runs(self, type_: str) -> TablesList:
        content = []
        for file in self.context.files_of_type(type_):
            content += file.content
        return content

    @property
    def header_runs(self) -> TablesList:
        return self._get_runs("header")

    @property
    def footer_runs(self) -> TablesList:
        return self._get_runs("footer")

    @property
    def officeDocument_runs(self) -> TablesList:
        return self._get_runs("officeDocument")

    @property
    def body_runs(self) -> TablesList:
        return self.officeDocument_runs

    @property
    def footnotes_runs(self) -> TablesList:
        return self._get_runs("footnotes")

    @property
    def endnotes_runs(self) -> TablesList:
        return self._get_runs("endnotes")

    @property
    def images(self) -> Dict[str, bytes]:
        return pull_image_files(self.context, self.docx2python_kwargs['image_folder'])
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
        if self.docx2python_kwargs['paragraph_styles'] is True:
            # Paragraph descriptors have been inserted as the first run of each
            # paragraph. Take them out.
            pars = [''.join(x[1:]) for x in iter_at_depth(self.document_runs, 4)]
            return '\n\n'.join(pars)
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

    # noinspection PyPep8Naming
    @property
    def core_properties(self) -> Dict[str, str]:
        """Document core-properties as a dictionary.

        Docx files created with Google docs won't have core-properties. If the file
        `core-properties` is missing, return an empty dict."""
        try:
            docProps = next(iter(self.context.files_of_type("core-properties")))
            return collect_docProps(docProps.root_element)
        except StopIteration:
            warn(
                "Could not find core-properties file (should be in docProps/core.xml) "
                "in DOCX, so returning an empty core_properties dictionary. Docx files "
                "created in Google Docs do not have a core-properties file, so this "
                "may be expected."
            )
            return {}

    def save_images(self, image_folder: str) -> Dict[str, bytes]:
        return pull_image_files(self.context, image_folder)
