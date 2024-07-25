"""Test methods of File object that are not tested elsewhere.

:author: Shay Hill
:created: 4/3/2021
"""

from docx2python.attribute_register import Tags, get_prefixed_tag
from docx2python.docx_reader import DocxReader
from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestFileObject:
    """
    Test methods of DocxContext object which are not tested elsewhere.
    """

    def test_get_content_full(self) -> None:
        """
        Return full content if no root given.
        """
        full_extraction = docx2python(RESOURCES / "example.docx")
        context = DocxReader(RESOURCES / "example.docx")
        assert (
            full_extraction.body_runs
            == context.file_of_type("officeDocument").get_text()
        )
        context.close()
        full_extraction.close()

    def test_get_content_partial(self) -> None:
        """
        Return content below root argument if given.
        """
        full_extraction = docx2python(RESOURCES / "example.docx")
        context = DocxReader(RESOURCES / "example.docx")
        document_xml = context.file_of_type("officeDocument")
        first_par = next(
            x
            for x in document_xml.root_element.iter()
            if get_prefixed_tag(x) == Tags.PARAGRAPH
        )
        assert [[[[full_extraction.body_runs[0][0][0][0]]]]] == document_xml.get_text(
            first_par
        )
        context.close()
        full_extraction.close()
