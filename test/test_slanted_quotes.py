#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test that Word's tilted quotes and double quotes extract Docx2Python."""

from docx2python.main import docx2python

from .conftest import RESOURCES


class TestTiltedQuotes:
    """ Confirming this works with v1.25 """

    def test_exact_representation(self) -> None:
        """Most characters are represented exactly"""
        pars = docx2python(RESOURCES / "slanted_quotes.docx")
        assert pars.text == '“double quote”\n\n‘single quote’\n\nApostrophe’s'
