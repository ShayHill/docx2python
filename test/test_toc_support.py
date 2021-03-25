#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Testing Table of Contents support as requested by user leboni

:author: Shay Hill
:created: 8/19/2020

User leboni forwarded a docx file, `zen_of_python.docx` with Table of Contents.
Addressing issue

`KeyError: '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'`

When attempting to extract content from such documents.

Two types of links in docx files. Internal links look like actual hyperlinks without
an href.

    <w:hyperlink w:anchor="_Toc48296956" w:history="1">
        <w:r w:rsidRPr="00810578">
            <w:rPr>
                <w:rStyle w:val="Hyperlink"/>
                <w:noProof/>
            </w:rPr>
            <w:t>Beautiful is better than ugly.</w:t>
        </w:r>
    </w:hyperlink>
"""

from docx2python.main import docx2python
import pytest


class TestTocText:
    @pytest.mark.xfail
    def test_get_toc_text(self) -> None:
        """Extract header text from table-of-contents header."""
        extraction = docx2python("resources/zen_of_python.docx")
        # TODO: remove trailing </a> tag for toc text
        assert docx2python("resources/zen_of_python.docx").text[:66] == (
            "Contents\n\n\tBeautiful is better than ugly."
            "\t1</a>\n\n\n\n\n\n\n\nBeautiful i"
        )
