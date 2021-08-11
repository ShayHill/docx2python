#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Libreoffice conversions from doc to docx raise CaretDepthError

:author: Shay Hill
:created: 8/11/2021

Uner shadowmimosa shared a docx (libreoffice_conversion.docx), converted by libreoffice
from a doc that raises a CaretDepthError.
"""


from docx2python.main import docx2python
import os


class TestLibreofficeConversion:
    def test_libreoffice_conversion(self) -> None:
        """Extracts text without a CaretDepthError"""
        extraction = docx2python(
            os.path.join("resources", "libreoffice_conversion.docx")
        )
        _ = extraction.document
