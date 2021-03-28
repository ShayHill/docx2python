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
from typing import Any, Dict

import pytest

from docx2python.docx_context import (
    collect_docProps,
    collect_numFmts,
    get_context,
    pull_image_files,
)

from docx2python.globs import DocxContext


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
        numId2numFmts = collect_numFmts(zipf.read("word/numbering.xml"))
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

    def test_gets_properties(self) -> None:
        """Retrieves properties from docProps"""
        zipf = zipfile.ZipFile("resources/example.docx")
        props = collect_docProps(zipf.read("docProps/core.xml"))
        assert props["creator"] == "Shay Hill"
        assert props["lastModifiedBy"] == "Shay Hill"


@pytest.fixture
def docx_context() -> Dict[str, Any]:
    """result of running strip_text.get_context"""
    zipf = zipfile.ZipFile("resources/example.docx")
    return get_context(zipf)


# noinspection PyPep8Naming
class TestGetContext:
    """Text strip_text.get_context """

    # TODO: refactor this test to assert result.core_properties
    # def test_docProp2text(self, docx_context) -> None:
    #     """All targets mapped"""
    #     zipf = zipfile.ZipFile("resources/example.docx")
    #     props = collect_docProps(zipf.read("docProps/core.xml"))
    #     assert docx_context["docProp2text"] == props

    def test_numId2numFmts(self, docx_context) -> None:
        """All targets mapped"""
        zipf = zipfile.ZipFile("resources/example.docx")
        numId2numFmts = collect_numFmts(zipf.read("word/numbering.xml"))
        assert docx_context["numId2numFmts"] == numId2numFmts

    def test_numId2count(self, docx_context) -> None:
        """All numIds mapped to a default dict defaulting to 0"""
        for numId in docx_context["numId2numFmts"]:
            assert isinstance(docx_context["numId2count"][numId], defaultdict)
            assert docx_context["numId2count"][numId][0] == 0

    def test_lists(self) -> None:
        """Pass silently when no numbered or bulleted lists."""
        zipf = zipfile.ZipFile("resources/basic.docx")
        context = get_context(zipf)
        assert "numId2numFmts" not in context
        assert "numId2count" not in context


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
        zipf = zipfile.ZipFile("resources/basic.docx")
        context = get_context(zipf)
        docx_context = DocxContext("resources/basic.docx")
        pull_image_files(docx_context, "delete_this/path/to/images")
        assert os.listdir("delete_this/path/to/images") == []
        # clean up
        shutil.rmtree("delete_this")
