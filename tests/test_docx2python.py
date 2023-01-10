"""Test full functionality of source_old

:author: Shay Hill
:created: 7/5/2019
"""
import os
import re
import shutil

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python

from .conftest import RESOURCES

OUTPUT = docx2python(RESOURCES / "example.docx")
HTML_OUTPUT = docx2python(RESOURCES / "example.docx", html=True)


class TestFormatting:
    """Nested list output string formatting"""

    def test_header(self) -> None:
        """Header text in correct location"""
        header_text = "".join(iter_at_depth(OUTPUT.header, 4))
        assert re.match(r"Header text----media/image\d+\.\w+----$", header_text)

    def test_footer(self) -> None:
        """Footer text in correct location"""
        footer_text = "".join(iter_at_depth(OUTPUT.footer, 4))
        assert re.match(r"Footer text----media/image\d+\.\w+----$", footer_text)

    def test_footnotes(self) -> None:
        """Footnotes extracted."""
        assert OUTPUT.footnotes_runs == [
            [
                [
                    [[]],
                    [[]],
                    [["footnote1)\t", " First footnote"]],
                    [["footnote2)\t", " Second footnote", "----media/image1.png----"]],
                ]
            ]
        ]

    def test_endnotes(self) -> None:
        """Endnotes extracted."""
        assert OUTPUT.endnotes_runs == [
            [
                [
                    [[]],
                    [[]],
                    [["endnote1)\t", " First endnote"]],
                    [["endnote2)\t", " Second endnote", "----media/image1.png----"]],
                ]
            ]
        ]

    def test_numbered_lists(self) -> None:
        """Sublists reset. Expected formatting."""

        assert OUTPUT.body[0][0][0] == [
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

    def test_bullets(self) -> None:
        """Expected bullet format and indent."""
        assert OUTPUT.body_runs[0][1][0] == [
            ["--\t", "bullet no indent"],
            ["\t--\t", "bullet indent 1"],
            ["\t\t--\t", "bullet indent 2"],
        ]

    def test_ignore_formatting(self) -> None:
        """Text formatting is stripped."""
        assert OUTPUT.body[0][2][0] == [
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
        assert OUTPUT.body[1] == [[["Nested"], ["Table"]], [["A"], ["B"]]]

    def test_tab_delimited(self) -> None:
        """Tabs converted to \t."""
        assert OUTPUT.body[2][1][0][0] == "Tab\tdelimited\ttext"

    def test_lt_gt(self) -> None:
        """> and < are not encoded."""
        assert OUTPUT.body[2][2][0][0] == "10 < 20 and 20 > 10"

    def test_text_outside_table(self) -> None:
        """Text outside table is its own table (also tests image marker)"""
        assert OUTPUT.body[3] == [
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
                    "----media/image2.jpg----",
                ]
            ]
        ]


class TestHtmlFormatting:
    """Font styles exported as HTML."""

    def test_lt_gt(self) -> None:
        """> and < encoded"""
        assert HTML_OUTPUT.body[2][2][0][0] == "10 &lt; 20 and 20 &gt; 10"

    def test_formatting_captured(self) -> None:
        """Text formatting converted to html."""
        assert HTML_OUTPUT.body[0][2][0] == [
            "<b>Bold</b>",
            "<i>Italics</i>",
            "<u>Underlined</u>",
            '<span style="font-size:40pt">Large Font</span>',
            '<span style="color:FF0000">Colored</span>',
            '<span style="color:FF0000;font-size:40pt">Large Colored</span>',
            '<span style="font-size:40pt"><b>Large Bold</b></span>',
            '<span style="font-size:40pt"><b><i><u>Large Bold Italics Underlined</u></i></b></span>',
        ]

    def test_paragraph_formatting(self) -> None:
        """Text formatting converted to html."""
        assert HTML_OUTPUT.body_runs[3] == [
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
                    ["----media/image2.jpg----"],
                ]
            ]
        ]


class TestImageDir:
    """Write images out to file given an image directory."""

    def test_pull_image_files(self) -> None:
        """Copy image files to output path."""
        docx2python(RESOURCES / "example.docx", "delete_this/path/to/images")
        assert os.listdir("delete_this/path/to/images") == ["image1.png", "image2.jpg"]
        # clean up
        shutil.rmtree("delete_this")


def test_header_runs() -> None:
    """Runs returned as separate strings. Paragraphs not joined"""
    assert docx2python(
        RESOURCES / "multiple_runs_per_paragraph.docx", html=True
    ).document_runs == [
        [[[["Multiple ", "<b>Runs in the</b>", " Header"]]]],
        [
            [
                [
                    [
                        "This document contains paragraphs with multiple runs per "
                        "paragraph. This ensures result.document and "
                        "result.document_runs return different things."
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
