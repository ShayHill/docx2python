"""Test full functionality of source_old

:author: Shay Hill
:created: 7/5/2019
"""

import os
import re
import shutil

from paragraphs import par

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python
from tests.conftest import RESOURCES

ALT_TEXT = par(
    """----Image alt text---->A close up of a logo\n\n
        Description automatically generated<"""
)


class TestFormatting:
    """Nested list output string formatting"""

    def test_header(self) -> None:
        """Header text in correct location"""
        with docx2python(RESOURCES / "example.docx") as output:
            header_text = "".join(iter_at_depth(output.header, 4))
            assert re.match(
                rf"Header text{ALT_TEXT}----media/image\d+\.\w+----$", header_text
            )

    def test_footer(self) -> None:
        """Footer text in correct location"""
        with docx2python(RESOURCES / "example.docx") as output:
            footer_text = "".join(iter_at_depth(output.footer, 4))
            assert re.match(
                rf"Footer text{ALT_TEXT}----media/image\d+\.\w+----$", footer_text
            )

    def test_footnotes(self) -> None:
        """Footnotes extracted."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.footnotes_runs == [
                [
                    [
                        [[]],
                        [[]],
                        [["footnote1)\t", " First footnote"]],
                        [
                            [
                                "footnote2)\t",
                                " Second footnote",
                                par(
                                    """----Image alt text---->A close up of a
                                    logo\n\nDescription automatically generated<"""
                                ),
                                "----media/image1.png----",
                            ]
                        ],
                    ]
                ]
            ]

    def test_endnotes(self) -> None:
        """Endnotes extracted."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.endnotes_runs == [
                [
                    [
                        [[]],
                        [[]],
                        [["endnote1)\t", " First endnote"]],
                        [
                            [
                                "endnote2)\t",
                                " Second endnote",
                                par(
                                    """----Image alt text---->A close up of a
                                    logo\n\nDescription automatically generated<"""
                                ),
                                "----media/image1.png----",
                            ]
                        ],
                    ]
                ]
            ]

    def test_numbered_lists(self) -> None:
        """Sublists reset. Expected formatting."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body[0][0][0] == [
                "I)\texpect I",
                "\tA)\texpect A",
                "\tB)\texpect B",
                "\t\t1)\texpect 1",
                "\t\t\ta)\texpect a",
                "\t\t\tb)\texpect b",
                "\t\t\t\t1)\texpect 1",
                "\t\t\t\t\ta)\texpect a",
                "\t\t\t\t\t\ti)\texpect i",
                "\t\t\t\t\t\tii)\texpect ii",
                "II)\tThis should be II",
                "\tA)\tThis should be A), not C)",
            ]

    def test_numbered_lists_with_custom_start_index(self) -> None:
        """Sublists start from non-default index. Expected formatting."""
        with docx2python(RESOURCES / "example_numbering.docx") as output:
            assert output.body[0][0][0] == [
                "II)\texpect II",
                "C)\texpect C",
                "D)\texpect D",
                "4)\texpect 4",
                "e)\texpect e",
                "f)\texpect f",
                "6)\texpect 6",
                "f)\texpect f",
                "viii)\texpect viii",
                "ix)\texpect ix",
                "",
                "",
            ]

    def test_bullets(self) -> None:
        """Expected bullet format and indent."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body_runs[0][1][0] == [
                ["--\t", "bullet no indent"],
                ["\t--\t", "bullet indent 1"],
                ["\t\t--\t", "bullet indent 2"],
            ]

    def test_ignore_formatting(self) -> None:
        """Text formatting is stripped."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body[0][2][0] == [
                "Bold",
                "Italics",
                "Underlined",
                "Large Font",
                "Colored",
                "Large Colored",
                "Large Bold",
                "Large Bold Italics Underlined",
            ]

    def test_nested_table(self) -> None:
        """Appears as a new table"""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body[1] == [[["Nested"], ["Table"]], [["A"], ["B"]]]

    def test_tab_delimited(self) -> None:
        """Tabs converted to \t."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body[2][1][0][0] == "Tab\tdelimited\ttext"

    def test_lt_gt(self) -> None:
        """> and < are not encoded."""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body[2][2][0][0] == "10 < 20 and 20 > 10"

    def test_text_outside_table(self) -> None:
        """Text outside table is its own table (also tests image marker)"""
        with docx2python(RESOURCES / "example.docx") as output:
            assert output.body[3] == [
                [
                    [
                        "Text outside table",
                        "Reference footnote 1----footnote1----",
                        "Reference footnote 2----footnote2----",
                        "Reference endnote 1----endnote1----",
                        "Reference endnote 2----endnote2----",
                        "Heading 1",
                        "Heading 2",
                        "",
                        "----Image alt text---->A jellyfish in water\n\n"
                        + "Description automatically generated"
                        + "<----media/image2.jpg----",
                    ]
                ]
            ]


class TestHtmlFormatting:
    """Font styles exported as HTML."""

    def test_lt_gt(self) -> None:
        """> and < encoded"""
        with docx2python(RESOURCES / "example.docx", html=True) as html_output:
            assert html_output.body[2][2][0][0] == "10 &lt; 20 and 20 &gt; 10"

    def test_formatting_captured(self) -> None:
        """Text formatting converted to html."""
        with docx2python(RESOURCES / "example.docx", html=True) as html_output:
            assert html_output.body[0][2][0] == [
                "<b>Bold</b>",
                "<i>Italics</i>",
                "<u>Underlined</u>",
                '<span style="font-size:40pt">Large Font</span>',
                '<span style="color:FF0000">Colored</span>',
                '<span style="color:FF0000;font-size:40pt">Large Colored</span>',
                '<span style="font-size:40pt"><b>Large Bold</b></span>',
                par(
                    """<span style="font-size:40pt"><b><i><u>Large Bold Italics
                    Underlined</u></i></b></span>"""
                ),
            ]

    def test_paragraph_formatting(self) -> None:
        """Text formatting converted to html."""
        with docx2python(RESOURCES / "example.docx", html=True) as html_output:
            expect = [
                [
                    [
                        ["Text outside table"],
                        ["Reference footnote 1", "----footnote1----"],
                        ["Reference footnote 2", "----footnote2----"],
                        ["Reference endnote 1", "----endnote1----"],
                        ["Reference endnote 2", "----endnote2----"],
                        ["<h1>", "Heading 1", "</h1>"],
                        ["<h2>", "Heading 2", "</h2>"],
                        [],
                        [
                            par(
                                """----Image alt text---->A jellyfish in
                                water\n\nDescription automatically generated<"""
                            ),
                            "----media/image2.jpg----",
                        ],
                    ]
                ]
            ]
            result = html_output.body_runs[3]
            assert result == expect


class TestImageDir:
    """Write images out to file given an image directory."""

    def test_pull_image_files(self) -> None:
        """Copy image files to output path."""
        pars = docx2python(RESOURCES / "example.docx", "delete_this/path/to/images")
        assert set(os.listdir("delete_this/path/to/images")) == {
            "image1.png",
            "image2.jpg",
        }
        # clean up
        shutil.rmtree("delete_this")
        pars.close()


def test_header_runs() -> None:
    """Runs returned as separate strings. Paragraphs not joined"""
    pars = docx2python(RESOURCES / "multiple_runs_per_paragraph.docx", html=True)
    assert pars.document_runs == [
        [[[["Multiple ", "<b>Runs in the</b>", " Header"]]]],
        [
            [
                [
                    [
                        "This document contains paragraphs with multiple runs per "
                        + "paragraph. This ensures result.document and "
                        + "result.document_runs return different things."
                    ],
                    [],
                    ["Multiple ", "<b>Runs in the</b>", " Body"],
                    ["Multiple ", "<b>Runs in the</b>", " Body"],
                    ["Multiple ", "<b>Runs in the</b>", " Body"],
                    ["Multiple ", "<b>Runs in the</b>", " Body"],
                    [],
                ]
            ]
        ],
        [[[["Multiple ", "<b>Runs in the</b>", " Footer"]]]],
        [[[[]], [[]]]],
        [[[[]], [[]]]],
    ]
    pars.close()
