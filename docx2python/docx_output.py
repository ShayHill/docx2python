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

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, cast
from warnings import warn

from typing_extensions import Self

from docx2python.depth_collector import get_par_strings
from docx2python.docx_context import collect_docProps
from docx2python.docx_text import flatten_text, new_depth_collector
from docx2python.iterators import enum_at_depth, get_html_map, iter_at_depth
from docx2python.namespace import get_attrib_by_qn

if TYPE_CHECKING:
    import os
    from types import TracebackType

    from docx2python.depth_collector import Par
    from docx2python.docx_reader import DocxReader

    ParsTable = List[List[List[List[Par]]]]
    TextTable = List[List[List[List[List[str]]]]]


def _join_runs(tables: TextTable) -> list[list[list[list[str]]]]:
    """Join the leaves of a 5-deep nested list of strings.

    :param str_tree: a 5-deep nested list of strings [[[[["a", "b"]]]]]
    :return: a 4-deep nexted list of strings [[[["ab"]]]]

    Collapse nested lists of run strings into nested lists of paragraph strings.

    runs = [
        [
            [
                [
                    [
                        "run1", "run2"
                    ],
                    [
                        "run3", "run4"
                    ]
                ]
            ]
        ]
    ]

    `join_runs(runs)` =>

    [
        [
            [
                [
                    "run1run2",
                    "run3run4"
                ]
            ]
        [
    ]
    """
    result: list[list[list[list[str]]]] = []
    for tbl in tables:
        result.append(cast(List[List[List[str]]], []))
        for row in tbl:
            result[-1].append(cast(List[List[str]], []))
            for cell in row:
                result[-1][-1].append(cast(List[str], []))
                for par in cell:
                    result[-1][-1][-1].append("".join(par))
    return result


@dataclass
class DocxContent:
    """Holds return values for docx content."""

    docx_reader: DocxReader
    image_folder: str | os.PathLike[str] | None

    def close(self):
        """Close the zipfile opened by DocxReader."""
        self.docx_reader.close()

    def __enter__(self) -> Self:
        """Do nothing. The zipfile will open itself when needed.

        :return: self
        """
        return self

    def __exit__(
        self,
        exc_type: None | type[BaseException],
        exc_value: None | BaseException,
        exc_traceback: None | TracebackType,
    ) -> None:
        """Close the zipfile opened by DocxReader.

        :param exc_type: Python internal use
        :param exc_value: Python internal use
        :param exc_traceback: Python internal use
        """
        self.close()

    def _get_pars(self, type_: str) -> ParsTable:
        """Get Par instances for an internal document type.

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes")
            You can try others.
        :return: text paragraphs [[[Par]]]
        """
        content: ParsTable = []
        for file in self.docx_reader.files_of_type(type_):
            content += file.content
        return content

    @property
    def header_pars(self) -> ParsTable:
        """Get nested Par instances for header files.

        :return: nested Par instances [[[Par]]]
        """
        return self._get_pars("header")

    @property
    def footer_pars(self) -> ParsTable:
        """Get nested Par instances for footer files.

        :return: nested Par instances [[[Par]]]
        """
        return self._get_pars("footer")

    @property
    def officeDocument_pars(self) -> ParsTable:
        """Get nested Par instances for the main officeDocument file.

        :return: nested Par instances [[[Par]]]
        """
        return self._get_pars("officeDocument")

    @property
    def body_pars(self) -> ParsTable:
        """Get nested Par instances for the main officeDocument file.

        :return: nested Par instances [[[Par]]]

        This is an alias for officeDocument_pars.
        """
        return self.officeDocument_pars

    @property
    def footnotes_pars(self) -> ParsTable:
        """Get nested Par instances for footnotes files.

        :return: nested Par instances [[[Par]]]
        """
        return self._get_pars("footnotes")

    @property
    def endnotes_pars(self) -> ParsTable:
        """Get nested Par instances for endnotes files.

        :return: nested Par instances [[[Par]]]
        """
        return self._get_pars("endnotes")

    @property
    def document_pars(self) -> ParsTable:
        """All docx x_pars properties concatenated.

        :return: nested Par instances [[[Par]]]
        """
        return (
            self.header_pars
            + self.body_pars
            + self.footer_pars
            + self.footnotes_pars
            + self.endnotes_pars
        )

    @property
    def header_runs(self) -> list[list[list[list[list[str]]]]]:
        """Get nested run strings for header files.

        :return: nested run strings [[[[[str]]]]]
        """
        return get_par_strings(self.header_pars)

    @property
    def footer_runs(self) -> list[list[list[list[list[str]]]]]:
        """Get nested run strings for footer files.

        :return: nested run strings [[[[[str]]]]]
        """
        return get_par_strings(self.footer_pars)

    @property
    def officeDocument_runs(self) -> list[list[list[list[list[str]]]]]:
        """Get nested run strings for the main officeDocument file.

        :return: nested run strings [[[[[str]]]]]
        """
        return get_par_strings(self.officeDocument_pars)

    @property
    def body_runs(self) -> list[list[list[list[list[str]]]]]:
        """Get nested run strings for the main officeDocument file.

        :return: nested run strings [[[[[str]]]]]

        This is an alias for officeDocument_runs.
        """
        return self.officeDocument_runs

    @property
    def footnotes_runs(self) -> list[list[list[list[list[str]]]]]:
        """Get nested run strings for footnotes files.

        :return: nested run strings [[[[[str]]]]]
        """
        return get_par_strings(self.footnotes_pars)

    @property
    def endnotes_runs(self) -> list[list[list[list[list[str]]]]]:
        """Get nested run strings for endnotes files.

        :return: nested run strings [[[[[str]]]]]
        """
        return get_par_strings(self.endnotes_pars)

    @property
    def document_runs(self) -> list[list[list[list[list[str]]]]]:
        """All docx x_runs properties concatenated.

        :return: nested run strings [[[[[str]]]]]
        """
        return (
            self.header_runs
            + self.body_runs
            + self.footer_runs
            + self.footnotes_runs
            + self.endnotes_runs
        )

    @property
    def header(self) -> list[list[list[list[str]]]]:
        """Get header text.

        :return: nested paragraphs [[[[str]]]]
        """
        return _join_runs(self.header_runs)

    @property
    def footer(self) -> list[list[list[list[str]]]]:
        """Get footer text.

        :return: nested paragraphs [[[[str]]]]
        """
        return _join_runs(self.footer_runs)

    @property
    def officeDocument(self) -> list[list[list[list[str]]]]:
        """Get officeDocument text.

        :return: nested paragraphs [[[[str]]]]
        """
        return _join_runs(self.officeDocument_runs)

    @property
    def body(self) -> list[list[list[list[str]]]]:
        """Get body text.

        :return: nested paragraphs [[[[str]]]]

        This is an alias for officeDocument.
        """
        return self.officeDocument

    @property
    def footnotes(self) -> list[list[list[list[str]]]]:
        """Get footnotes text.

        :return: nested paragraphs [[[[str]]]]
        """
        return _join_runs(self.footnotes_runs)

    @property
    def endnotes(self) -> list[list[list[list[str]]]]:
        """Get endnotes text.

        :return: nested paragraphs [[[[str]]]]
        """
        return _join_runs(self.endnotes_runs)

    @property
    def document(self) -> list[list[list[list[str]]]]:
        """All docx x properties concatenated.

        :return: nested paragraphs [[[[str]]]]
        """
        return self.header + self.body + self.footer + self.footnotes + self.endnotes

    @property
    def images(self) -> dict[str, bytes]:
        """Get bytestring of all images in the document.

        :return: dict {image_name: image_bytes}
        """
        return self.docx_reader.pull_image_files(self.image_folder)

    @property
    def text(self) -> str:
        r"""All docx paragraphs, "\n\n" joined.

        :return: all docx paragraphs, "\n\n" joined
        """
        return flatten_text(self.document_runs)

    @property
    def html_map(self) -> str:
        """A visual mapping of docx content.

        :return: html to show all strings with index tuples
        """
        return get_html_map(self.document_runs)

    @property
    def properties(self) -> dict[str, str | None]:
        """Document core-properties as a dictionary.

        :return: document core-properties as a dictionary

        Docx files created with Google docs won't have core-properties. If the file
        `core-properties` is missing, return an empty dict.
        """
        warn(
            "DocxContent.properties is deprecated and will be removed in some future "
            + "version. Use DocxContent.core_properties.",
            FutureWarning,
            stacklevel=2,
        )
        return self.core_properties

    @property
    def core_properties(self) -> dict[str, str | None]:
        """Document core-properties as a dictionary.

        :return: document core-properties as a dictionary

        Docx files created with Google docs won't have core-properties. If the file
        `core-properties` is missing, return an empty dict.
        """
        try:
            docProps = next(iter(self.docx_reader.files_of_type("core-properties")))
            return collect_docProps(docProps.root_element)
        except StopIteration:
            warn(
                "Could not find core-properties file (should be in docProps/core.xml) "
                + "in DOCX, so returning an empty core_properties dictionary. Docx "
                + "files created in Google Docs do not have a core-properties file, "
                + "so this may be expected.",
                stacklevel=2,
            )
            return {}

    @property
    def comments(self) -> list[tuple[str, str, str, str]]:
        """Get comments from the docx file.

        :return: tuples of (reference_text, author, date, comment_text)
        """
        office_document = self.docx_reader.file_of_type("officeDocument")
        depth_collector = office_document.depth_collector
        comment_ranges = depth_collector.comment_ranges
        comment_elements = self.docx_reader.comments

        if len(comment_ranges) != len(comment_elements):
            msg = (
                "comment_ranges and comment_elements have different lengths. "
                + "Failed to extract comments."
            )
            warn(msg, stacklevel=2)
            return []

        if not comment_elements:
            return []

        try:
            comments_file = self.docx_reader.file_of_type("comments")
        except KeyError:
            return []

        all_runs = list(enum_at_depth(get_par_strings(office_document.content), 5))
        comments: list[tuple[str, str, str, str]] = []
        for comment in comment_elements:
            id_ = get_attrib_by_qn(comment, "w:id")
            author = get_attrib_by_qn(comment, "w:author")
            date = get_attrib_by_qn(comment, "w:date")

            tree = new_depth_collector(comments_file, comment).tree_text
            tree_pars = ["".join(x) for x in iter_at_depth(tree, 4)]
            comment_text = "\n\n".join(tree_pars)

            beg_ref, end_ref = comment_ranges[id_]
            reference = "".join(y for _, y in all_runs[beg_ref:end_ref])

            comments.append((reference, author, date, comment_text))
        return comments

    def save_images(self, image_folder: str) -> dict[str, bytes]:
        """Write images to hard drive.

        :param image_folder: folder to write images to
        :return: dictionary of image names and image data

        If the image folder does not exist, it will not be created.
        """
        return self.docx_reader.pull_image_files(image_folder)
