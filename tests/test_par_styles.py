""" Par styles converted to flags

:author: Shay Hill
:created: 3/18/2021

"""

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestParStyles:
    def test_par_styles(self) -> None:
        """
        If do_html, paragraphs style is the first element of every paragraph

        If no paragraph style, empty string is first element of evert paragraph

        :return:
        """
        with docx2python(RESOURCES / "example.docx") as extraction:
            document_pars = extraction.document_pars
        styled = [(p.style, p.run_strings) for p in iter_at_depth(document_pars, 4)]
        styled = [x for x in styled if x[1]]
        expect = [
            (
                "Header",
                [
                    "Header text",
                    "----Image alt text---->A close up of a logo\n\n"
                    + "Description automatically generated<",
                    "----media/image1.png----",
                ],
            ),
            ("ListParagraph", ["I)\t", "expect I"]),
            ("ListParagraph", ["\tA)\t", "expect A"]),
            ("ListParagraph", ["\tB)\t", "expect B"]),
            ("ListParagraph", ["\t\t1)\t", "expect 1"]),
            ("ListParagraph", ["\t\t\ta)\t", "expect a"]),
            ("ListParagraph", ["\t\t\tb)\t", "expect b"]),
            ("ListParagraph", ["\t\t\t\t1)\t", "expect 1"]),
            ("ListParagraph", ["\t\t\t\t\ta)\t", "expect a"]),
            ("ListParagraph", ["\t\t\t\t\t\ti)\t", "expect i"]),
            ("ListParagraph", ["\t\t\t\t\t\tii)\t", "expect ii"]),
            ("ListParagraph", ["II)\t", "This should be II"]),
            ("ListParagraph", ["\tA)\t", "This should be A), not C)"]),
            ("ListParagraph", ["--\t", "bullet no indent"]),
            ("ListParagraph", ["\t--\t", "bullet indent 1"]),
            ("ListParagraph", ["\t\t--\t", "bullet indent 2"]),
            ("", ["Bold"]),
            ("", ["Italics"]),
            ("", ["Underlined"]),
            ("", ["Large Font"]),
            ("", ["Colored"]),
            ("", ["Large Colored"]),
            ("", ["Large Bold"]),
            ("", ["Large Bold Italics Underlined"]),
            ("", ["Nested"]),
            ("", ["Table"]),
            ("", ["A"]),
            ("", ["B"]),
            ("", ["Tab", "\t", "delimited", "\t", "text"]),
            ("", ["10 < 20 and 20 > 10"]),
            ("", ["Text outside table"]),
            ("", ["Reference footnote 1", "----footnote1----"]),
            ("", ["Reference footnote 2", "----footnote2----"]),
            ("", ["Reference endnote 1", "----endnote1----"]),
            ("", ["Reference endnote 2", "----endnote2----"]),
            ("Heading1", ["Heading 1"]),
            ("Heading2", ["Heading 2"]),
            (
                "",
                [
                    "----Image alt text---->A jellyfish in water\n\n"
                    + "Description automatically generated<",
                    "----media/image2.jpg----",
                ],
            ),
            (
                "Footer",
                [
                    "Footer text",
                    "----Image alt text---->A close up of a logo\n\n"
                    + "Description automatically generated<",
                    "----media/image1.png----",
                ],
            ),
            ("FootnoteText", ["footnote1)\t", " First footnote"]),
            (
                "FootnoteText",
                [
                    "footnote2)\t",
                    " Second footnote",
                    "----Image alt text---->A close up of a logo\n\n"
                    + "Description automatically generated<",
                    "----media/image1.png----",
                ],
            ),
            ("EndnoteText", ["endnote1)\t", " First endnote"]),
            (
                "EndnoteText",
                [
                    "endnote2)\t",
                    " Second endnote",
                    "----Image alt text---->A close up of a logo\n\n"
                    + "Description automatically generated<",
                    "----media/image1.png----",
                ],
            ),
        ]
        assert styled == expect
