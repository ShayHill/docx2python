"""Test loading a .docx from a buffer of raw bytes.

:author: Shay Hill
:created: 2024-07-25
"""

from io import BytesIO
from pathlib import Path

from docx2python.main import docx2python
from tests.conftest import RESOURCES

example_docx = RESOURCES / "example.docx"


class TestFromBytes:
    def test_from_bytes(self) -> None:
        """Loads .docx from a buffer of raw bytes."""
        with Path(example_docx).open("rb") as f:
            buf = BytesIO(f.read())
        with docx2python(buf) as content:
            core_properties = content.core_properties
            expected = {
                "title": None,
                "subject": None,
                "creator": "Shay Hill",
                "keywords": None,
                "description": None,
                "lastModifiedBy": "Shay Hill",
            }
            for prop, value in expected.items():
                assert core_properties[prop] == value
