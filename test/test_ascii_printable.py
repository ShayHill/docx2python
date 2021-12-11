#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test that most characters in string.printable can are represented (some are
altered) in Docx2Python output. """

from docx2python.main import docx2python
import string


class TestAsciiPrintable:
    """ Confirming this works with v1.25 """

    def test_exact_representation(self) -> None:
        """Most characters are represented exactly"""
        pars = docx2python("resources/ascii_printable.docx")
        assert pars.text[:-3] == string.printable[:-3]

    def test_line_feed(self) -> None:
        """A carriage return becomes a linefeed"""
        pars = docx2python("resources/ascii_printable.docx")
        assert string.printable[-3] == '\r'
        assert pars.text[-3] == '\n'

    def test_vertical_tab(self) -> None:
        """A vertical_tab becomes a linefeed"""
        pars = docx2python("resources/ascii_printable.docx")
        assert string.printable[-2] == '\x0b'
        assert pars.text[-2] == '\n'

    def test_form_feed(self) -> None:
        """A form_feed becomes a linefeed"""
        pars = docx2python("resources/ascii_printable.docx")
        assert string.printable[-1] == '\x0c'
        assert pars.text[-1] == '\n'
