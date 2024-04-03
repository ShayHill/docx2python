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

from docx2python.docx_context import collect_docProps

from .docx_text import flatten_text, new_depth_collector
from .iterators import enum_at_depth, get_html_map, iter_at_depth, join_leaves
from .namespace import qn

if TYPE_CHECKING:
    from .docx_reader import DocxReader
    from .docx_text import TablesList


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
        Create depth-four paragraph tables from depth-five run tables.

        :param name: name of an internal docx xml file
        :return: extracted text from named file with runs joined together into
            paragraphs.
        :raise AttributeError: if "name" file cannot be found

        Docx2Python v1 joined runs into paragraphs [[[str]]] earlier in the code.
        Docx2Python v2 exposes runs [[[[str]]]] to the user, but still returns
        paragraphs by default.
        """
        if name in {"header", "footer", "body", "footnotes", "endnotes"}:
            runs = getattr(self, name + "_runs")
            return join_leaves("", runs, 4)
        msg = f"no attribute {name}"
        raise AttributeError(msg)

    def _get_runs(self, type_: str) -> TablesList:
        """Get text runs for an internal document type.

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes")
            You can try others.
        :return: text runs [[[[str]]]]
        """
        content: TablesList = []
        for file in self.docx_reader.files_of_type(type_):
            content += file.content
        return content

    @property
    def header_runs(self) -> TablesList:
        """Get text runs for header files.

        :return: text runs [[[[str]]]]
        """
        return self._get_runs("header")

    @property
    def footer_runs(self) -> TablesList:
        """Get text runs for footer files.

        :return: text runs [[[[str]]]]
        """
        return self._get_runs("footer")

    @property
    def officeDocument_runs(self) -> TablesList:
        """Get text runs for the main officeDocument file.

        :return: text runs [[[[str]]]]
        """
        return self._get_runs("officeDocument")

    @property
    def body_runs(self) -> TablesList:
        """Get text runs for the main officeDocument file.

        :return: text runs [[[[str]]]]

        This is an alias for officeDocument_runs.
        """
        return self.officeDocument_runs

    @property
    def footnotes_runs(self) -> TablesList:
        """Get text runs for footnotes files.

        :return: text runs [[[[str]]]]
        """
        return self._get_runs("footnotes")

    @property
    def endnotes_runs(self) -> TablesList:
        """Get text runs for endnotes files.

        :return: text runs [[[[str]]]]
        """
        return self._get_runs("endnotes")

    @property
    def images(self) -> dict[str, bytes]:
        """Get bytestring of all images in the document.

        :return: dict {image_name: image_bytes}
        """
        return self.docx_reader.pull_image_files(
            self.docx2python_kwargs["image_folder"]
        )

    @property
    def document(self) -> TablesList:
        """All docx "tables" concatenated.

        :return: text paragraphs [[[str]]]
        """
        return self.header + self.body + self.footer + self.footnotes + self.endnotes

    @property
    def document_runs(self) -> TablesList:
        """All docx x_runs properties concatenated.

        :return: text runs [[[[str]]]]
        """
        return (
            self.header_runs
            + self.body_runs
            + self.footer_runs
            + self.footnotes_runs
            + self.endnotes_runs
        )

    @property
    def text(self) -> str:
        r"""All docx paragraphs, "\n\n" joined.

        :return: all docx paragraphs, "\n\n" joined
        """
        do_pStyle = self.docx2python_kwargs["paragraph_styles"]
        return flatten_text(self.document_runs, do_pStyle)

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

        all_runs = list(enum_at_depth(office_document.content, 5))
        comments: list[tuple[str, str, str, str]] = []
        for comment in comment_elements:
            id_ = comment.attrib[qn("w:id")]

            author = comment.attrib[qn("w:author")]
            date = comment.attrib[qn("w:date")]

            tree = new_depth_collector(comments_file, comment).tree
            tree_pars = ["".join(x) for x in iter_at_depth(tree, 4)]
            comment_text = "\n\n".join(tree_pars)

            beg_ref, end_ref = comment_ranges[id_]
            reference = "".join(x.value for x in all_runs[beg_ref:end_ref])

            comments.append((reference, author, date, comment_text))
        return comments

    def save_images(self, image_folder: str) -> dict[str, bytes]:
        """Write images to hard drive.

        :param image_folder: folder to write images to
        :return: dictionary of image names and image data

        If the image folder does not exist, it will not be created.
        """
        return self.docx_reader.pull_image_files(image_folder)
