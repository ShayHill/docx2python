#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test hyperlink functionality

:author: Shay Hill
:created: 4/19/2020
"""

from docx2python.main import docx2python
import os

# TODO: fix hyperlink runs. The following produces runs:
# [
#     [
#         [
#             [
#                 [
#                     "This is a link to ",
#                     '<a href="http://www.shayallenhill.com/">',
#                     "my we",
#                     "b",
#                     "site",
#                     "</a>",
#                     ".",
#                 ]
#             ]
#         ]
#     ]
# ]


class TestHyperlink:
    def test_prints(self) -> None:
        """Pull the text of the hyperlink"""
        extraction = docx2python(os.path.join("resources", "hyperlink.docx"))
        assert (
            '<a href="http://www.shayallenhill.com/">my website</a>' in extraction.text
        )
