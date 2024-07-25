"""Test features of DocxContent that weren't tested in test_docx2python.

:author: Shay Hill
:created: 7/6/2019
"""

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestDocument:
    def test_combine_of_header_body_footer(self) -> None:
        """Return all content combined as instance.document"""
        with docx2python(RESOURCES / "example.docx") as content:
            assert (
                content.document
                == content.header
                + content.body
                + content.footer
                + content.footnotes
                + content.endnotes
            )

    def test_read_only(self) -> None:
        """Document attribute is read only."""
        with docx2python(RESOURCES / "example.docx") as content:
            doc1 = content.document
            doc1 = doc1[:1]
            assert doc1 != content.document
            assert (
                content.document
                == content.header
                + content.body
                + content.footer
                + content.footnotes
                + content.endnotes
            )


class TestText:
    def test_function(self) -> None:
        r"""Return '\n\n'-delimited paragraphs as instance.text."""
        with docx2python(RESOURCES / "example.docx") as content:
            assert content.text == "\n\n".join(iter_at_depth(content.document, 4))


class TestHtmlMap:
    def test_function(self) -> None:
        """Return html tables."""
        with docx2python(RESOURCES / "example.docx") as content:
            assert (
                content.html_map[:48]
                == '<html><body><table border="1"><tr><td><pre>(0, 0'
            )
