"""A simple test for docx files saved with the strict menu option.

:author: Shay Hill
:created: 2024-07-02
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestParagraphsOnly:
    """Confirming this works with v1.25"""

    def test_paragraphs_only(self) -> None:
        """Run without issue"""
        pars = docx2python(RESOURCES / "strict.docx")
        assert pars.document == [
            [[["--\tBullet1", "--\tBullet2", "1)\tNumber1", "2)\tNumber2"]]],
            [[["Cellaa"], ["Cellab"]], [["Cellba"], ["Cellbb"]]],
            [[[""]]],
        ]
