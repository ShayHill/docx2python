"""Test that most characters in string.printable can are represented

(some are altered) in Docx2Python output.
"""

import string

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestAsciiPrintable:
    """Confirming this works with v1.25"""

    def test_exact_representation(self) -> None:
        """Most characters are represented exactly
        The last seven characters are
        \n\r\x0b\b0cEND
        \n \r \x0b and \x0c are ignored by word when typed.
        END is there (added by hand to docx file) to let me know I'm past any
        trailing characters
        """
        with docx2python(RESOURCES / "ascii_printable.docx") as pars:
            assert pars.text[:-7] == string.printable[:-4]

    def test_html_true(self) -> None:
        """Most characters are represented exactly. &, <, and > are escaped.

        The last seven characters are
        \n\r\x0b\b0cEND
        \n \r \x0b and \x0c are ignored by word when typed.
        END is there (added by hand to docx file) to let me know I'm past any
        trailing characters
        """
        pars = docx2python(RESOURCES / "ascii_printable.docx", html=True)
        assert pars.text[:-7] == (
            '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&amp'
            ";'()*+,-./:;&lt;=&gt;?@[\\]^_`{|}~ \t"
        )
        pars.close()
