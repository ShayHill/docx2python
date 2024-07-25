"""Test opening docx reader and closing it.

Closing a DocxReader or DocxContent instance will close the zipfile openend when the
DocxReader instance was created.

:author: Shay Hill
:created: 7/5/2019
"""

import pytest

from docx2python.attribute_register import Tags, get_prefixed_tag
from docx2python.docx_reader import DocxReader
from docx2python.main import docx2python
from tests.conftest import RESOURCES

example_docx = RESOURCES / "example.docx"
example_copy_docx = RESOURCES / "example_copy.docx"


class TestCloseDocxReader:
    def test_explicit_close(self) -> None:
        """Closing DocxReader closes the zipfile."""
        input_context = DocxReader(example_docx)
        _ = input_context.file_of_type("officeDocument").root_element
        # assert DocxReader zipfile is open
        assert input_context._DocxReader__zipf.fp  # type: ignore

        input_context.close()
        # assert DocxReader zipfile is closed
        assert not input_context._DocxReader__zipf.fp  # type: ignore

    def test_no_access_after_explicit_close(self) -> None:
        """The zipfile will not automatically reopen after explicit close."""
        input_context = DocxReader(example_docx)
        input_context.close()
        # assert zipfile cannot be accessed
        with pytest.raises(ValueError):
            _ = input_context.zipf


class TestDocxReaderContext:
    def test_context_manager_enter(self):
        """DocxReader can be used as a context manager."""
        with DocxReader(example_docx) as input_context:
            input_xml = input_context.file_of_type("officeDocument").root_element
            assert get_prefixed_tag(input_xml) == Tags.DOCUMENT

    def test_context_manager_close(self):
        """DocxReader can be used as a context manager."""
        with DocxReader(example_docx) as input_context:
            _ = input_context.file_of_type("officeDocument").root_element
        with pytest.raises(ValueError):
            _ = input_context.zipf


class TestCloseDocxContent:
    def test_explicit_close(self) -> None:
        """Closing DocxReader closes the zipfile."""
        content = docx2python(example_docx)
        _ = content.header_runs
        assert content.docx_reader._DocxReader__zipf.fp  # type: ignore

        content.close()
        # assert DocxReader zipfile is closed
        assert not content.docx_reader._DocxReader__zipf.fp  # type: ignore

    def test_no_access_after_explicit_close(self) -> None:
        """The zipfile will not automatically reopen after explicit close."""
        content = docx2python(example_docx)
        content.close()
        # assert zipfile cannot be accessed
        with pytest.raises(ValueError):
            _ = content.docx_reader.zipf


class TestDocxContentContext:
    def test_context_manager_enter(self):
        """DocxReader can be used as a context manager."""
        with docx2python(example_docx) as content:
            _ = content.header_runs

    def test_context_manager_close(self):
        """DocxReader can be used as a context manager."""
        with docx2python(example_docx) as content:
            pass
            _ = content.header_runs
        with pytest.raises(ValueError):
            _ = content.docx_reader.zipf
