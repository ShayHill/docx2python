#!/usr/bin/env python3

from io import BytesIO

from docx2python.main import docx2python

from .conftest import RESOURCES

example_docx = RESOURCES / "example.docx"


class TestFromBytes:
    def test_from_bytes(self) -> None:
        """Loads .docx from a buffer of raw bytes."""
        buf = BytesIO(open(example_docx, "rb").read())
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
