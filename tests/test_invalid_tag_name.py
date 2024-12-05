"""Issue 72: Invalid tag name.

User makretch found a file converted by Aspose that had an invalid tag name in a
comment. This tag name caused a ValueError when passed to `etree.QName`.

ValueError: Invalid tag name 'cyfunction Comment at 0x12345678abcd'

I addressed this by skipping elements with invalid tag names and raising a warning.

:author: Shay Hill
:created: 2024-12-05
"""

import pytest
from conftest import RESOURCES

from docx2python import docx2python


class TestInvalidTagName:
    """Confirming this works with v1.25"""

    def test_invalid_tag_name(self) -> None:
        """Pass if no ValueError is raised."""
        extraction = docx2python(RESOURCES / "invalid_tag_name.docx")
        with pytest.warns(UserWarning, match="skipping invalid tag name"):
            _ = extraction.text
        extraction.close()
