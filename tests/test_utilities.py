"""DocxReader object is able to open a docx file, search and replace text, then save.

:author: Shay Hill
:created: 2021-12-20

This test opens a file on your hd, edits it, then saves it with the filename
"pears_and_apples.docx".
"""

from docx2python.main import docx2python
from docx2python.utilities import get_headings, get_links, replace_docx_text

from .conftest import RESOURCES


class TestSearchReplace:
    def test_search_and_replace(self) -> None:
        """Apples -> Pears, Pears -> Apples

        Ignore html differences when html is False"""
        html = False
        input_filename = RESOURCES / "apples_and_pears.docx"
        output_filename = RESOURCES / "pears_and_apples.docx"
        with docx2python(input_filename, html=html) as input_doc:
            assert input_doc.text == (
                "Apples and Pears\n\nPears and Apples\n\n"
                "Apples and Pears\n\nPears and Apples"
            )
        replace_docx_text(
            input_filename,
            output_filename,
            ("Apples", "Bananas"),
            ("Pears", "Apples"),
            ("Bananas", "Pears"),
            html=html,
        )
        with docx2python(output_filename, html=html) as output_doc:
            assert output_doc.text == (
                "Pears and Apples\n\nApples and Pears\n\n"
                "Pears and Apples\n\nApples and Pears"
            )

    def test_ampersand(self) -> None:
        """Apples -> Pears, Pears -> Apples

        Replace text with an ampersand"""
        html = False
        input_filename = RESOURCES / "apples_and_pears.docx"
        output_filename = RESOURCES / "pears_and_apples.docx"
        with docx2python(input_filename, html=html) as input_doc:
            assert input_doc.text == (
                "Apples and Pears\n\nPears and Apples\n\n"
                "Apples and Pears\n\nPears and Apples"
            )
        replace_docx_text(
            input_filename,
            output_filename,
            ("Apples", "Apples & Pears <>"),
            html=html,
        )
        with docx2python(output_filename, html=html) as output_doc:
            assert output_doc.text == (
                "Apples & Pears <> and Pears\n\nPears and Apples & Pears <>\n\n"
                "Apples & Pears <> and Pears\n\nPears and Apples & Pears <>"
            )

    def test_search_and_replace_html(self) -> None:
        """Apples -> Pears, Pears -> Apples

        Exchange strings when formatting is consistent across the string. Leave
        alone otherwise.
        """
        html = True
        input_filename = RESOURCES / "apples_and_pears.docx"
        output_filename = RESOURCES / "pears_and_apples.docx"
        with docx2python(input_filename, html=html) as input_doc:
            assert input_doc.text == (
                "Apples and Pears\n\n"
                "Pears and Apples\n\n"
                'Apples and <span style="background-color:green">Pears</span>\n\n'
                "Pe<b>a</b>rs and Apples"
            )
        replace_docx_text(
            input_filename,
            output_filename,
            ("Apples", "Bananas"),
            ("Pears", "Apples"),
            ("Bananas", "Pears"),
            html=html,
        )
        with docx2python(output_filename, html=html) as output_doc:
            assert output_doc.text == (
                "Pears and Apples\n\n"
                "Apples and Pears\n\n"
                'Pears and <span style="background-color:green">Apples</span>\n\n'
                "Pe<b>a</b>rs and Pears"
            )


def test_get_links() -> None:
    """Return links as tuples"""
    assert [x for x in get_links(RESOURCES / "merged_links.docx")] == [
        ("https://www.shayallenhill.com", "hy"),
        ("https://www.shayallenhill.com", "per"),
        ("https://www.shayallenhill.com", "link"),
        ("https://www.shayallenhill.com", "hyperlink"),
    ]


def test_get_headings() -> None:
    """Return all headings (paragraphs with heading style) in document"""
    assert [x for x in get_headings(RESOURCES / "example.docx")] == [
        ["Heading1", "Heading 1"],
        ["Heading2", "Heading 2"],
    ]
