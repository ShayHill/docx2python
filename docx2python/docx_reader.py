"""Hold and decode docx internal xml files.

:author: Shay Hill
:created: 3/18/2021

See the docx file structure in ``README_DOCX_FILE_STRUCTURE.md``. Each file in that
structure can be stored as a ``File`` instance, though not all will be stored through
the typical docx2python progression.

The ``File`` class is designed to hold and decode xml files with content (text).
Several of the xml files in a docx do not contain content. These contain numbering
formats, font information, rId-lookup tables, and other. ``File`` instances will hold
these as well, though they will not have ``rels`` or ``content`` attributes. Will
return an empty dictionary or empty list if asked.

Some of these non-content files are shared between between . The substance of these
files is accessible through the ``DocxContent`` class. This class holds file
instances and decodes shared non-content in a docx file structure.
"""

from __future__ import annotations

import copy
import os
import zipfile
from contextlib import suppress
from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING, List
from warnings import warn

from lxml import etree
from typing_extensions import Self

from docx2python import depth_collector
from docx2python.attribute_register import XML2HTML_FORMATTER
from docx2python.docx_context import NumIdAttrs, collect_numAttrs, collect_rels
from docx2python.docx_text import get_file_content, new_depth_collector
from docx2python.merge_runs import merge_elems

ParsTable = List[List[List[List[depth_collector.Par]]]]
TextTable = List[List[List[List[List[str]]]]]

if TYPE_CHECKING:
    from io import BytesIO
    from types import TracebackType

    from lxml.etree import _Element as EtreeElement  # type: ignore

    from docx2python.depth_collector import DepthCollector

CONTENT_FILE_TYPES = {"officeDocument", "header", "footer", "footnotes", "endnotes"}


@dataclass
class File:
    """The attribute dict of a file in the docx, plus cached data.

    The docx lists internal files in various _rels files. Each will be specified with a
    dict of, e.g.::

        {
            'Id': 'rId8',
            'Type': 'http://schemas.openxmlformats.org/.../relationships/header',
            'Target': 'header1.xml'
        }

    This isn't quite enough to infer the structure of the docx. You'll also need to
    know the directory where each attribute dict was found::

        'dir': 'word/_rels'

    That's the starting point for these instances. Other attributes are inferred or
    created at runtime.
    """

    def __init__(self, context: DocxReader, attribute_dict: dict[str, str]) -> None:
        """Point to container DocxContext instance and store attributes as properties.

        :param context: The DocxContent object holding this instance
        :param attribute_dict: Attributes of this file found in the rels, plus 'dir' as
            described above.
        """
        self.context = context
        self.Id = str(attribute_dict["Id"])
        self.Type = Path(attribute_dict["Type"]).name
        self.Target = attribute_dict["Target"]
        self.dir = attribute_dict["dir"]

        # cached_properties
        self.__path: None | str = None
        self.__rels_path: None | str = None
        self.__rels: None | dict[str, str] = None
        self.__root_element: None | EtreeElement = None
        self.__depth_collector: None | DepthCollector = None

    def __repr__(self) -> str:
        """File with self.path.

        :return: String representation
        """
        return f"File({self.path})"

    @property
    def path(self) -> str:
        """Infer path/to/xml/file from instance attributes.

        :return: path to xml file

        This will take the information in a file specification (from one of the rels
        files, e.g., {Id:'  ', Type:'  ' Target:'  ', dir:'  '}) and infer a path to
        the specified xml file.

        E.g.,
        from     self.dir = '_rels'       self.Target = 'word/document.xml
                    dirname ''          +       dirname 'word/'
                                        +       filename =   'document.xml'
        return `word/document`

        E.g.,
        from     self.dir = 'word/_rels'       self.Target = 'header1.xml
                    dirname 'word'      +            dirname ''
                                        +       filename =   'header1.xml'
        return `word/header1.xml`
        """
        if self.__path is not None:
            return self.__path

        dirs = [Path(x).parent.name for x in (self.dir, self.Target)]
        dirname = "/".join([x for x in dirs if x])
        filename = Path(self.Target).name
        self.__path = f"{dirname}/{filename}"
        return self.__path

    @property
    def _rels_path(self) -> str:
        """Infer path/to/rels from instance attributes.

        :return: path to rels (which may not exist)

        Every content file (``document.xml``, ``header1.xml``, ...) will have its own
        ``.rels`` file--if any relationships are defined.

        The path inferred here may not exist.

        E.g.,
        from     self.dir = '_rels'       self.Target = 'word/document.xml
                    dirname ''          +       dirname 'word/'
                                        +       filename =   'document.xml'
        return `word/_rels/document.xml.rels`

        E.g.,
        from     self.dir = 'word/_rels'       self.Target = 'header1.xml
                    dirname 'word'      +            dirname ''
                                        +       filename =   'header1.xml'
        return `word/_rels/header1.xml.rels`
        """
        if self.__rels_path is not None:
            return self.__rels_path
        dirname, filename = os.path.split(self.path)
        self.__rels_path = "/".join([dirname, "_rels", filename + ".rels"])
        return self.__rels_path

    @property
    def rels_element(self) -> EtreeElement | None:
        """Root element of the rels file.

        :return: Root element of the rels file.
        :raise KeyError: If the rels file is not found
        """
        rels_files = [x for x in self.context.files if x.Target == self._rels_path]
        if len(rels_files) == 1:
            return rels_files[0].root_element
        return None

    @property
    def rels(self) -> dict[str, str]:
        """Get rIds mapped to values.

        :return: dict of rIds mapped to values

        Each content file.xml will have a file.xml.rels file--if relationships are
        defined. Inside file.xml, values defined in the file.xml.rels file may be
        referenced by their rId numbers.

        :return: Contents of the file.xml.rels file with reference rId numbers. These
        refer to values defined in the file.xml.rels file:

        E.g.::

        {
            "rId3": "webSettings.xml",
            "rId2": "settings.xml",
            "rId1": "styles.xml",
            "rId6": "theme/theme1.xml",
            "rId5": "fontTable.xml",
            "rId4": "https://www.shayallenhill.com/",
        }

        Not every xml file with have a rels file. Return an empty dictionary if the
        rels file is not found.
        """
        rels_element = self.rels_element
        if rels_element is not None:
            return {str(x.attrib["Id"]): str(x.attrib["Target"]) for x in rels_element}
        return {}

    @property
    def root_element(self) -> EtreeElement:
        """Root element of the file.

        :return: Root element of the file.

        Try to merge consecutive, duplicate (except text) elements in content files.
        See documentation for ``merge_elems``. Warn if ``merge_elems`` fails.
        (I don't think it will fail).
        """
        if self.__root_element is not None:
            return self.__root_element

        root = etree.fromstring(self.context.zipf.read(self.path))
        if self.Type in CONTENT_FILE_TYPES:
            root_ = copy.copy(root)
            try:
                merge_elems(self, root)
            except (TypeError, AttributeError) as ex:
                warn(
                    "Attempt to merge consecutive elements in "
                    + f"{self.context.docx_filename} {self.path} resulted in "
                    + f"{ex!r}. Moving on.",
                    stacklevel=2,
                )
                self.__root_element = root_
        self.__root_element = root
        return self.__root_element

    @property
    def depth_collector(self) -> DepthCollector:
        """DepthCollector instance for this file.

        :return: DepthCollector instance for this file.

        The DepthCollector instance will be used to extract text from the file.
        """
        self.__depth_collector = self.__depth_collector or new_depth_collector(self)
        return self.__depth_collector

    @property
    def content(self) -> ParsTable:
        """Text extracted into a 4-deep nested list of Par instances.

        :return: [[[[Par]]]]
        """
        return self.get_content()

    @property
    def text(self) -> TextTable:
        """Text extracted into a 5-deep list of strings [[[[[str]]]]].

        :return: Text extracted into a nested list of strings [[[[[str]]]]]
        """
        return self.get_text()

    def get_content(self, root: EtreeElement | None = None) -> ParsTable:
        """Return the same content as property 'content' with optional given root.

        :param root: Extract content of file from root down.
            If root is not given, return full content of file.
        :return: Text extracted into [[[[Par]]]]
        """
        if root is None:
            return self.depth_collector.tree
        return get_file_content(self, root)

    def get_text(self, root: EtreeElement | None = None) -> TextTable:
        """Return the same content as property 'text' with optional given root.

        :param root: Extract content of file from root down.
            If root is not given, return full content of file.
        :return: Text extracted into [[[[[str]]]]]
        """
        return depth_collector.get_par_strings(self.get_content(root))


@dataclass
class DocxReader:
    """Hold File instances and decode info shared between them (e.g., numFmts)."""

    def __init__(
        self,
        docx_filename: str | os.PathLike[str] | BytesIO,
        *,
        html: bool = False,
        duplicate_merged_cells: bool = True,
    ) -> None:
        """Initialize DocxReader instance.

        :param docx_filename: Path to docx file, or BytesIO object.
        :param html: If True, convert xml to html.
        :param paragraph_styles: If True, include paragraph styles in html.
        :param duplicate_merged_cells: If True, duplicate text in merged cells.
        """
        self.docx_filename = docx_filename
        self.duplicate_merged_cells = duplicate_merged_cells

        if html:
            self.xml2html_format = XML2HTML_FORMATTER
        else:
            self.xml2html_format = {}

        # cached properties and a flag (__closed)
        self.__zipf: None | zipfile.ZipFile = None
        self.__files: None | list[File] = None
        self.__numId2Attrs: None | dict[str, list[NumIdAttrs]] = None
        self.__closed = False

    @property
    def zipf(self) -> zipfile.ZipFile:
        """Entire docx unzipped into bytes.

        :return: Entire docx unzipped into bytes.
        :raise ValueError: If DocxReader instance has been closed
        """
        if self.__closed:
            msg = "DocxReader instance has been closed."
            raise ValueError(msg)
        if self.__zipf is None:
            self.__zipf = zipfile.ZipFile(self.docx_filename)
            return self.__zipf
        return self.__zipf

    def close(self):
        """Close the zipfile, set __closed flag to True."""
        if self.__zipf is not None and self.__zipf.fp:
            self.__zipf.close()
        self.__closed = True

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
    ) -> Self:
        """Close the zipfile.

        :param exc_type: Python internal use
        :param exc_value: Python internal use
        :param exc_traceback: Python internal use
        """
        self.close()
        return self

    @property
    def files(self) -> list[File]:
        """Instantiate a File instance for every content file.

        :return: List of File instances, one per content file.
        """
        if self.__files is not None:
            return self.__files

        files: list[File] = []
        for k, v in collect_rels(self.zipf).items():
            dir_ = str(Path(k).parent)
            files += [File(self, {**x, "dir": dir_}) for x in v]
        self.__files = files
        return self.__files

    @property
    def comments(self) -> list[EtreeElement]:
        """Comments from the document.

        :return: Comments from the document.
        """
        try:
            comment_file = self.file_of_type("comments")
        except KeyError:
            return []
        return list(comment_file.root_element)

    @property
    def numId2Attrs(self) -> dict[str, list[NumIdAttrs]]:
        """Return numId referenced in xml to list of NumIdAttrs per indentation level.

        :return: numId referenced in xml to list of NumIdAttrs per indentation level

        See docstring for collect_numAttrs

        Returns an empty dictionary if word/numbering.xml cannot be found.
        Ultimately, this will result in any lists (there should NOT be any lists if
        there is no word/numbering.xml) being "numbered" with "--".
        """
        if self.__numId2Attrs is not None:
            return self.__numId2Attrs

        try:
            numFmts_root = etree.fromstring(self.zipf.read("word/numbering.xml"))
            self.__numId2Attrs = collect_numAttrs(numFmts_root)
        except KeyError:
            self.__numId2Attrs = {}
        return self.__numId2Attrs

    def file_of_type(self, type_: str) -> File:
        """Return file instance attrib Type='http://.../type_'. Warn if more than one.

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes")
            You can try others.
        :return: File instance of the requested type
        :raise KeyError: if no file of the requested type is found
        """
        files_of_type = self.files_of_type(type_)
        if len(files_of_type) > 1:
            warn(
                "Multiple files of type '{type_}' found. Returning first.", stacklevel=2
            )
        try:
            return files_of_type[0]
        except IndexError as exc:
            raise KeyError(
                f"There is no item of type '{type_}' "
                + "in the {self.docx_filename} archive"
            ) from exc

    def files_of_type(self, type_: str | None = None) -> list[File]:
        """List File instances with attrib Type='http://.../type_'.

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes", "comments")
            You can try others. If argument is None (default), returns all content file
            types.
        :return: File instances of the requested type, sorted by path
        """
        types = CONTENT_FILE_TYPES if type_ is None else {type_}
        return sorted(
            (x for x in self.files if x.Type in types), key=attrgetter("path")
        )

    def content_files(self) -> list[File]:
        """List content files (contain displayed text) inside the docx.

        :return: File instances of context files, sorted by path
        """
        return self.files_of_type()

    def save(self, filename: str | os.PathLike[str]) -> None:
        """Save the (presumably altered) xml.

        :param filename: path to output file (presumably *.docx)

        xml (root_element) attributes are cached, so these can be altered and saved.
        This allows saving a copy of the input docx after the ``merge_elems``
        operation. Also allows some light editing like search and replace.
        """
        overwrite = [*CONTENT_FILE_TYPES, "relationships"]
        content_files = [x for x in self.files if x.Type in overwrite]
        with zipfile.ZipFile(f"{filename}", mode="w") as zout:
            _copy_but(self.zipf, zout, {x.path for x in content_files})
            for file in content_files:
                zout.writestr(file.path, etree.tostring(file.root_element))

    def pull_image_files(
        self, image_directory: str | os.PathLike[str] | None = None
    ) -> dict[str, bytes]:
        """Copy images from zip file.

        :param image_directory: optional destination for copied images
        :return: Image names mapped to images in binary format.

            To write these to disc::

                with open(key, 'wb') as file:
                    file.write(value)

        :side effects: Given an optional image_directory, will write the images out
        to file.
        """
        images: dict[str, bytes] = {}
        for image in self.files_of_type("image"):
            with suppress(KeyError):
                images[Path(image.Target).name] = self.zipf.read(image.path)
        if image_directory is not None:
            image_directory = Path(image_directory)
            image_directory.mkdir(parents=True, exist_ok=True)
            for file, image_bytes in images.items():
                with (image_directory / file).open("wb") as image_copy:
                    _ = image_copy.write(image_bytes)
        return images


def _copy_but(
    in_zip: zipfile.ZipFile,
    out_zip: zipfile.ZipFile,
    exclusions: set[str] | None = None,
) -> None:
    """Copy every file in a docx except those listed in exclusions.

    :param in_zip: zipfile of origin xml file
    :param out_zip: zipfile of destination xml file
    :param exclusions: filenames you don't want to copy (e.g., 'document.xml')
    """
    exclusions = exclusions or set()
    for item in in_zip.infolist():
        if item.filename not in exclusions:
            buffer = in_zip.read(item.filename)
            out_zip.writestr(item, buffer)
