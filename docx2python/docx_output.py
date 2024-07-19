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
from typing import TYPE_CHECKING, Any
from warnings import warn

from typing_extensions import Self

from docx2python.depth_collector import get_par_strings
from docx2python.docx_context import collect_docProps
from docx2python.docx_text import flatten_text, new_depth_collector
from docx2python.iterators import (
    enum_at_depth,
    get_html_map,
    iter_at_depth,
    join_leaves,
)
from docx2python.namespace import get_attrib_by_qn

if TYPE_CHECKING:
    from typing import List

    from docx2python.depth_collector import Par
    from docx2python.docx_reader import DocxReader

    ParsTable = List[List[List[List[Par]]]]


@dataclass
class DocxContent:
    """Holds return values for docx content."""

    docx_reader: DocxReader
    docx2python_kwargs: dict[str, Any]

    def close(self):
        """Close the zipfile opened by DocxReader"""
        self.docx_reader.close()

    def __enter__(self) -> Self:
        """Do nothing. The zipfile will open itself when needed.

        :return: self
        """
        return self

    def __exit__(
        self,
        exc_type: Any,  # None | Type[Exception], but py <= 3.9 doesn't like it.
        exc_value: Any,  # None | Exception, but py <= 3.9 doesn't like it.
        exc_traceback: Any,  # None | TracebackType, but py <= 3.9 doesn't like it.
    ) -> None:
        """Close the zipfile opened by DocxReader

        :param exc_type: Python internal use
        :param exc_value: Python internal use
        :param exc_traceback: Python internal use
        """
        self.close()

    def __getattr__(self, name: str) -> Any:
        """
        Create sub-attributes for docx content.

        :param name: name of an internal docx xml file
        :return: extracted text from named file with runs joined together into
            paragraphs.
        :raise AttributeError: if "name" file cannot be found

        For supported docx content file types (header, footer, body (officeDocument),
        footnotes, endnotes, documents), return docx 1.0 style paragraphs [[[str]]],
        attribute_runs [[[[str]]]] or attribute_pars [[[Par]]] as appropriate.

        Docx2Python v1 joined runs into paragraphs [[[str]]] earlier in the code.

        Docx2Python v2 exposes runs [[[[str]]]] to the user, but still returns
        paragraphs by default.

        Docx2Python v3 exposes Par and Run instances to the user, access these as
        header_pars, footer_pars, etc.
        """
        if name in {
            "header",
            "footer",
            "officeDocument",
            "body",
            "footnotes",
            "endnotes",
            "document",
        }:
            runs = getattr(self, name + "_runs")
            return join_leaves("", runs, 4)
        if name in {
            "header_runs",
            "footer_runs",
            "officeDocument_runs",
            "body_runs",
            "footnotes_runs",
            "endnotes_runs",
            "document_runs",
        }:
            pars = getattr(self, name[:-5] + "_pars")
            return get_par_strings(pars)
        msg = f"no attribute {name}"
        raise AttributeError(msg)

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
    def images(self) -> dict[str, bytes]:
        """Get bytestring of all images in the document.

        :return: dict {image_name: image_bytes}
        """
        return self.docx_reader.pull_image_files(
            self.docx2python_kwargs["image_folder"]
        )

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
        return get_html_map(self.document)

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
                + "so this may be expected."
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
            warn(msg)
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
