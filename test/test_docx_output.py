#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test features of DocxContent that weren't tested in test_docx2python.

:author: Shay Hill
:created: 7/6/2019
"""

from docx2python.main import docx2python

INST = docx2python("resources/example.docx")


class TestDocument:
    def test_combine_of_header_body_footer(self) -> None:
        """Return all content combined as instance.document """
        assert INST.document == INST.header + INST.body + INST.footer

    def test_read_only(self) -> None:
        """Document attribute is read only."""
        doc1 = INST.document
        doc1 = doc1[:1]
        assert doc1 != INST.document
        assert INST.document == INST.header + INST.body + INST.footer


class TestText:
    def test_function(self) -> None:
        """Return '\n\n'-delimited paragraphs as instance.text. """
        assert INST.text[:50] == (
            "Header text\n\nI)	expect I\n" "\n	A)	expect A\n\n	B)	expect"
        )
        assert INST.text[-50:] == (
            "\nText outside table----image1.jpg----\n\nFooter text"
        )
