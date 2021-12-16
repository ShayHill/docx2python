#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test docx2python.docx_context.py

author: Shay Hill
created: 6/26/2019
"""
import os
import zipfile
from tempfile import TemporaryDirectory

from lxml import etree

from docx2python.attribute_register import Tags
from docx2python.docx_reader import DocxReader
from docx2python.docx_context import collect_numFmts
from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python


class TestSaveDocx:
    def test_save_unchanged(self) -> None:
        """Creates a valid docx"""
        input_context = DocxReader("resources/example.docx")
        input_xml = input_context.file_of_type("officeDocument").root_element
        input_context.save("resources/example_copy.docx")
        output_context = DocxReader("resources/example_copy.docx")
        output_xml = output_context.file_of_type("officeDocument").root_element
        assert etree.tostring(input_xml) == etree.tostring(output_xml)

    def test_save_changed(self) -> None:
        """Creates a valid docx and updates text"""
        input_context = DocxReader("resources/example.docx")
        input_xml = input_context.file_of_type("officeDocument").root_element
        for elem in (x for x in input_xml.iter() if x.tag == Tags.TEXT):
            if not elem.text:
                continue
            elem.text = elem.text.replace("bullet", "BULLET")
        input_context.save("resources/example_edit.docx")
        output_content = DocxReader("resources/example_edit.docx")
        output_runs = output_content.file_of_type("officeDocument").content
        output_text = "".join(iter_at_depth(output_runs, 5))
        assert "bullet" not in output_text
        assert "BULLET" in output_text


class TestCollectNumFmts:
    """Test strip_text.collect_numFmts"""

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
            etree.fromstring(zipf.read("word/numbering.xml"))
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
    """Test strip_text.collect_docProps"""

    def test_gets_properties(self) -> None:
        """Retrieves properties from docProps"""
        core_properties = docx2python("resources/example.docx").core_properties
        expected = {
            "title": None,
            "subject": None,
            "creator": "Shay Hill",
            "keywords": None,
            "description": None,
            "lastModifiedBy": "Shay Hill",
        }
        for prop, value in expected.items():
            assert core_properties[prop] == value


# noinspection PyPep8Naming
class TestGetContext:
    """Text strip_text.get_context"""

    def test_numId2numFmts(self) -> None:
        """All targets mapped"""
        docx_context = DocxReader("resources/example.docx")
        assert docx_context.numId2numFmts == collect_numFmts(
            etree.fromstring(docx_context.zipf.read("word/numbering.xml"))
        )

    def test_lists(self) -> None:
        """Pass silently when no numbered or bulleted lists."""
        docx_context = DocxReader("resources/basic.docx")
        assert docx_context.numId2numFmts == {}


class TestPullImageFiles:
    """Test strip_text.pull_image_files"""

    def test_pull_image_files(self) -> None:
        """Copy image files to output path."""
        docx_context = DocxReader("resources/example.docx")
        with TemporaryDirectory() as image_folder:
            docx_context.pull_image_files(image_folder)
            assert os.listdir(image_folder) == ["image1.png", "image2.jpg"]

    def test_no_image_files(self) -> None:
        """Pass silently when no image files."""

        docx_context = DocxReader("resources/basic.docx")
        with TemporaryDirectory() as image_folder:
            docx_context.pull_image_files(image_folder)
            assert os.listdir(image_folder) == []
