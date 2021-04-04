#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Hold and decode docx internal xml files.

:author: Shay Hill
:created: 3/18/2021

See the docx file structure in ``README_DOCX_FILE_STRUCTURE.md``. Each file in that
structure can be stored as a ``File`` instance, though not all will be stored through
the typical docx2python progression. The ``File`` class is designed to hold and decode
xml files with content (text). Several, even most, of the xml files in a docx do not
contain content. These contain numbering formats, font information, rId-lookup
tables, and other. ``File`` instances will hold these as well, though they will not
have ``rels`` or ``content`` attributes.

Some of these non-content files are shared. The substance of these files is accessible
through the ``DocxContent`` class. This class holds file instances and decodes shared
non-content in a docx file structure.
"""
from __future__ import annotations

import os
import zipfile
from dataclasses import dataclass
from functools import cached_property
from operator import attrgetter
from typing import Dict, List, Optional, Union
from warnings import warn

from lxml import etree

from .docx_context import collect_numFmts, collect_rels
from .docx_text import get_text, merge_elems

CONTENT_FILE_TYPES = {"officeDocument", "header", "footer", "footnotes", "endnotes"}


@dataclass
class File:
    """
    The attribute dict of a file in the docx, plus cached data

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

    That's the starting point for these instances
    """

    def __init__(self, context: DocxContext, attribute_dict: Dict[str, str]) -> None:
        """
        Point to container DocxContext instance and store attributes as properties.

        :param context: The DocxContent object holding this instance
        :param attribute_dict: Attributes of this file found in the rels, plus 'dir' as
        described above.
        """
        self.context = context
        self.Id = attribute_dict["Id"]
        self.Type = os.path.basename(attribute_dict["Type"])
        self.Target = attribute_dict["Target"]
        self.dir = attribute_dict["dir"]

    def __repr__(self) -> str:
        """
        File with self.path
        """
        return f"File({self.path})"

    @cached_property
    def path(self) -> str:
        """
        Infer path/to/xml/file from instance attributes

        :returns: path to xml file

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
        dirs = [os.path.dirname(x) for x in (self.dir, self.Target)]
        dirname = "/".join([x for x in dirs if x])
        filename = os.path.basename(self.Target)
        return "/".join([dirname, filename])

    @cached_property
    def _rels_path(self) -> str:
        """
        Infer path/to/rels from instance attributes

        :returns: path to rels (which may not exist)

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
        dirname, filename = os.path.split(self.path)
        return "/".join([dirname, "_rels", filename + ".rels"])

    @cached_property
    def rels(self) -> Dict[str, Dict[str, str]]:
        """
        rIds mapped to values

        Each content file.xml will have a file.xml.rels file--if relationships are
        defined. Inside file.xml, values defined in the file.xml.rels file may be
        referenced by their rId numbers.

        :returns: Contents of the file.xml.rels file with reference rId numbers. These
        refer to values defined in the file.xml.rels file:

        E.g.::

        {
            "rId3": "webSettings.xml",
            "rId2": "settings.xml",
            "rId1": "styles.xml",
            "rId6": "theme/theme1.xml",
            "rId5": "fontTable.xml",
            "rId4": "http://www.shayallenhill.com/",
        }

        Not every xml file with have a rels file. Return an empty dictionary if the
        rels file is not found.
        """
        try:
            unzipped = self.context.zipf.read(self._rels_path)
            tree = etree.fromstring(unzipped)
            return {x.attrib["Id"]: x.attrib["Target"] for x in tree}
        except KeyError:
            return {}

    @cached_property
    def root_element(self) -> etree.Element:
        """
        Root element of the file.

        Try to merge consecutive, duplicate (except text) elements. Warn if fails.
        """
        root = etree.fromstring(self.context.zipf.read(self.path))
        if self.Type in CONTENT_FILE_TYPES:
            try:
                merge_elems(self, root)
            except Exception as ex:
                warn(
                    f"Attempt to merge consecutive elements in "
                    f"{self.context.docx_filename} {self.path} resulted in "
                    f"{repr(ex)}. Moving on."
                )
        return root

    @property
    def content(self) -> List[Union[List, str]]:
        """
        Text extracted into a 5-layer-deep nested list of strings.
        """
        return get_text(self)

    def get_content(
        self, root: Optional[etree.Element] = None
    ) -> List[Union[List, str]]:
        """
        The same content as property 'content' with optional given root.

        :param root: Extract content of file from root down.
            If root is not given, return full content of file.
        """
        return get_text(self, root)


@dataclass
class DocxContext:
    """
    Hold File instances and decode information shared between them (e.g., numFmts)
    """

    def __init__(
        self,
        docx_filename: str,
        image_folder: Optional[str] = None,
        html: bool = False,
        paragraph_styles: bool = False,
        extract_image: bool = True,
    ):
        self.docx_filename = docx_filename
        self.image_folder = image_folder
        self.do_html = html
        self.do_pStyle = paragraph_styles
        self.extract_image = extract_image

    @cached_property
    def zipf(self) -> zipfile.ZipFile:
        """
        Entire docx unzipped into bytes.
        """
        return zipfile.ZipFile(self.docx_filename)

    @cached_property
    def files(self) -> List[File]:
        """
        Instantiate a File instance for every content file.
        """
        files = []
        for k, v in collect_rels(self.zipf).items():
            files += [File(self, {**x, "dir": os.path.dirname(k)}) for x in v]
        return files

    # noinspection PyPep8Naming
    @cached_property
    def numId2numFmts(self) -> Dict[str, List[str]]:
        """
        numId referenced in xml to list of numFmt per indentation level

        See docstring for collect_numFmts

        Returns an empty dictionary is word/numbering.xml cannot be found.
        Ultimately, this will result in any lists (there should NOT be any lists if
        there is no word/numbering.xml) being "numbered" with "--".
        """
        try:
            numFmts_root = etree.fromstring(self.zipf.read("word/numbering.xml"))
            return collect_numFmts(numFmts_root)
        except KeyError:
            return {}

    def file_of_type(self, type_: str) -> File:
        """
        Return file instance attrib Type='http://.../type_'. Warn if more than one.

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes")
            You can try others.
        :return: File instance of the requested type
        """
        files_of_type = self.files_of_type(type_)
        if len(files_of_type) > 1:
            warn("Multiple files of type '{type_}' found. Returning first.")
        try:
            return files_of_type[0]
        except IndexError:
            raise KeyError(
                f"There is no item of type '{type_}' "
                "in the {self.docx_filename} archive"
            )

    def files_of_type(self, type_: str) -> List[File]:
        """
        File instances with attrib Type='http://.../type_'

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes")
            You can try others.
        :return: File instances of the requested type, sorted by path
        """
        return sorted(
            (x for x in self.files if x.Type == type_), key=attrgetter("path")
        )

    # TODO: improve docstring
    def save(self, filename: str) -> None:
        """
        Save the (presumably altered) xml.

        :param filename:
        :return:
        """
        content_files = [x for x in self.files if x.Type in CONTENT_FILE_TYPES]
        with zipfile.ZipFile(f"{filename}", mode="w") as zout:
            copy_but(self.zipf, zout, {x.path for x in content_files})
            for file in content_files:
                zout.writestr(file.path, etree.tostring(file.root_element))


# TODO: document and find a place for this helper function
def copy_but(inzip, outzip, exclusions=()):
    for item in inzip.infolist():
        if item.filename not in exclusions:
            buffer = inzip.read(item.filename)
            outzip.writestr(item, buffer)


# TODO: refactor entire project to lxml
