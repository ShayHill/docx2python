"""Test that Word's tilted quotes and double quotes extract Docx2Python."""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestTiltedQuotes:
    """Confirming this works with v1.25"""

    def test_exact_representation(self) -> None:
        """Most characters are represented exactly"""
        with docx2python(RESOURCES / "slanted_quotes.docx") as pars:
            assert pars.text == "“double quote”\n\n‘single quote’\n\nApostrophe’s"
