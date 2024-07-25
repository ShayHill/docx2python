""" Libreoffice conversions from doc to docx raise CaretDepthError

:author: Shay Hill
:created: 8/11/2021

Uner shadowmimosa shared a docx (libreoffice_conversion.docx), converted by libreoffice
from a doc that raises a CaretDepthError.
"""

import pytest

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestLibreofficeConversion:
    def test_libreoffice_conversion(self) -> None:
        """Extracts text without a CaretDepthError

        This test file for a user just happens to be in Chinese and contains an
        unsupported Chinese numbering format, hence the ``pytest.warns`` context.
        """
        with docx2python(RESOURCES / "libreoffice_conversion.docx") as content:
            with pytest.warns(UserWarning):
                _ = content.document
