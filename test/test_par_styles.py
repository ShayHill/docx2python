#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Par styles converted to flags

:author: Shay Hill
:created: 3/18/2021

"""

from docx2python.main import docx2python

OUTPUT = docx2python("resources/example.docx", paragraph_styles=True)


class TestParStyles:
    def test_par_styles(self) -> None:
        """
        If do_html, paragraphs style is the first element of every run

        :return:
        """
        assert OUTPUT.document_runs == [
            [[[["Header"]]]],
            [[[["Header"]]]],
            [[[["Header", "Header text", "----media/image1.png----"]]]],
            [
                [
                    [
                        ["ListParagraph", "I)\t", "expect I"],
                        ["ListParagraph", "\tA)\t", "expect A"],
                        ["ListParagraph", "\tB)\t", "expect B"],
                        ["ListParagraph", "\t\t1)\t", "expect 1"],
                        ["ListParagraph", "\t\t\ta)\t", "expect a"],
                        ["ListParagraph", "\t\t\tb)\t", "expect b"],
                        ["ListParagraph", "\t\t\t\t1)\t", "expect 1"],
                        ["ListParagraph", "\t\t\t\t\ta)\t", "expect a"],
                        ["ListParagraph", "\t\t\t\t\t\ti)\t", "expect i"],
                        ["ListParagraph", "\t\t\t\t\t\tii)\t", "expect ii"],
                        ["ListParagraph", "II)\t", "This should be II"],
                        ["ListParagraph", "\tA)\t", "This should be A), not C)"],
                    ]
                ],
                [
                    [
                        ["ListParagraph", "--\t", "bullet no indent"],
                        ["ListParagraph", "\t--\t", "bullet indent 1"],
                        ["ListParagraph", "\t\t--\t", "bullet indent 2"],
                    ]
                ],
                [
                    [
                        ["Bold"],
                        ["Italics"],
                        ["Underlined"],
                        ["Large Font"],
                        ["Colored"],
                        ["Large Colored"],
                        ["Large Bold"],
                        ["Large Bold Italics Underlined"],
                    ]
                ],
                [],
            ],
            [[[["Nested"]], [["Table"]]], [[["A"]], [["B"]]]],
            [
                [[[]]],
                [[["Tab", "\t", "delimited", "\t", "text"]]],
                [[["10 < 20 and 20 > 10"]]],
            ],
            [
                [
                    [
                        ["Text outside table"],
                        ["Reference footnote 1", "----footnote1----"],
                        ["Reference footnote 2", "----footnote2----"],
                        ["Reference endnote 1", "----endnote1----"],
                        ["Reference endnote 2", "----endnote2----"],
                        ["Heading1", "Heading 1"],
                        ["Heading2", "Heading 2"],
                        [],
                        ["----media/image2.jpg----"],
                    ]
                ]
            ],
            [[[["Footer"]]]],
            [[[["Footer", "Footer text", "----media/image1.png----"]]]],
            [[[["Footer"]]]],
            [
                [
                    [[]],
                    [[]],
                    [["footnote1)\t"]],
                    [["FootnoteText", " First footnote"]],
                    [["footnote2)\t"]],
                    [["FootnoteText", " Second footnote", "----media/image1.png----"]],
                ]
            ],
            [
                [
                    [[]],
                    [[]],
                    [["endnote1)\t"]],
                    [["EndnoteText", " First endnote"]],
                    [["endnote2)\t"]],
                    [["EndnoteText", " Second endnote", "----media/image1.png----"]],
                ]
            ],
        ]
