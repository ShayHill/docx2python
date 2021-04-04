#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test docx2python.docx_context.py

author: Shay Hill
created: 6/26/2019
"""
import os
import shutil
import zipfile
from collections import defaultdict
from xml.etree import ElementTree
from docx2python.docx_organization import DocxContext

import pytest

from docx2python.docx_context import (
    collect_docProps,
    collect_numFmts,
    pull_image_files,
)
from docx2python.docx_organization import DocxContext


class TestDocxContextObject:
    """
    Test methods of DocxContext object which are not tested elsewhere.
    """

    def test_file_of_type_exactly_one(self) -> None:
        """
        Return single file instance of type_ argument.
        """
        context = DocxContext("resources/example.docx")
        assert len(context.files_of_type("officeDocument")) == 1
        assert context.file_of_type("officeDocument").path == "word/document.xml"

    def test_file_of_type_more_than_one(self) -> None:
        """
        Warn when multiple file instances of type_ argument.
        """
        context = DocxContext("resources/example.docx")
        assert len(context.files_of_type("header")) == 3
        with pytest.warns(UserWarning):
            first_header = context.file_of_type("header")
        assert first_header.path == "word/header1.xml"

    def test_file_of_type_zero(self) -> None:
        """
        Raise KeyError when no file instances of type_ are found.
        """
        context = DocxContext("resources/example.docx")
        with pytest.raises(KeyError):
            first_header = context.file_of_type("invalid_type")


class TestCollectNumFmts:
    """Test strip_text.collect_numFmts """

    # noinspection PyPep8Naming
    def test_gets_formats(self) -> None:
        """Retrieves formats from example.docx

        This isn't a great test. There are numbered lists I've added then removed as
        I've edited my test docx. These still appear in the docx file. I could
        compare directly with the extracted numbering xml file, but even then I'd be
        comparing to something I don't know to be accurate. This just tests that all
        numbering formats are represented.
        """
        zipf = zipfile.ZipFile("resources/example.docx")
        numId2numFmts = collect_numFmts(
            ElementTree.fromstring(zipf.read("word/numbering.xml"))
        )
        formats = {x for y in numId2numFmts.values() for x in y}
        assert formats == {
            "lowerLetter",
            "upperLetter",
            "lowerRoman",
            "upperRoman",
            "bullet",
            "decimal",
        }


class TestCollectDocProps:
    """Test strip_text.collect_docProps """

    pass

    # TODO: restore test
    # def test_gets_properties(self) -> None:
    #     """Retrieves properties from docProps"""
    #     zipf = zipfile.ZipFile("resources/example.docx")
    #     props = collect_docProps(zipf.read("docProps/core.xml"))
    #     assert props["creator"] == "Shay Hill"
    #     assert props["lastModifiedBy"] == "Shay Hill"


# noinspection PyPep8Naming
class TestGetContext:
    """Text strip_text.get_context """

    # TODO: refactor this test to assert result.core_properties
    # def test_docProp2text(self, docx_context) -> None:
    #     """All targets mapped"""
    #     zipf = zipfile.ZipFile("resources/example.docx")
    #     props = collect_docProps(zipf.read("docProps/core.xml"))
    #     assert docx_context["docProp2text"] == props

    def test_numId2numFmts(self) -> None:
        """All targets mapped"""
        docx_context = DocxContext("resources/example.docx")
        assert docx_context.numId2numFmts == collect_numFmts(
            ElementTree.fromstring(docx_context.zipf.read("word/numbering.xml"))
        )

    def test_lists(self) -> None:
        """Pass silently when no numbered or bulleted lists."""
        docx_context = DocxContext("resources/basic.docx")
        assert docx_context.numId2numFmts == {}


class TestPullImageFiles:
    """Test strip_text.pull_image_files """

    def test_pull_image_files(self) -> None:
        """Copy image files to output path."""
        docx_context = DocxContext("resources/example.docx")
        pull_image_files(docx_context, "delete_this/path/to/images")
        assert os.listdir("delete_this/path/to/images") == ["image1.png", "image2.jpg"]
        # TODO: create a temp file for this function
        # clean up
        shutil.rmtree("delete_this")

    def test_no_image_files(self) -> None:
        """Pass silently when no image files."""
        # TODO: remove unneeded after refactoring pull_image_files signature
        docx_context = DocxContext("resources/basic.docx")
        pull_image_files(docx_context, "delete_this/path/to/images")
        assert os.listdir("delete_this/path/to/images") == []
        # clean up
        shutil.rmtree("delete_this")
