"""Try to use replace text with a linebreak.

:author: Shay Hill
:created: 2023-04-26
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestText:
    def test_user_checked_dropdown0(self) -> None:
        """Get checked-out box glyph and second dd entry"""
        extraction = docx2python(RESOURCES / "checked_drop1.docx")
        assert extraction.body_runs == [[[[["☒", " "], ["PIlihan A"]]]]]
        extraction.close()
