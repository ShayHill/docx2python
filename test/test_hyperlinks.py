#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test hyperlink functionality

:author: Shay Hill
:created: 4/19/2020
"""

from main import docx2python
import os


class TestHyperlink:
    def test_prints(self) -> None:
        """Pull the text of the hyperlink"""
        extraction = docx2python(os.path.join("resources", "hyperlink.docx"))
        assert (
            '<a href="http://www.shayallenhill.com/">my website</a>' in extraction.text
        )
