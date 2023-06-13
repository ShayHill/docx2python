""" Par styles converted to flags

:author: Shay Hill
:created: 3/18/2021

"""

from docx2python.main import docx2python

from .conftest import RESOURCES


class TestParStyles:
    def test_par_styles(self) -> None:
        """
        If do_html, paragraphs style is the first element of every paragraph

        If no paragraph style, empty string is first element of evert paragraph

        :return:
        """
        content = docx2python(RESOURCES / "example.docx", paragraph_styles=True)
        assert content.document_runs == [
            [[[["Header"]]]],
            [[[["Header",
                "Header text",
                "----Image alt text---->A close up of a logo\n\nDescription automatically generated<",
                "----media/image1.png----"]]]],
            [[[["Header"]]]],
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
                        ["None", "Bold"],
                        ["None", "Italics"],
                        ["None", "Underlined"],
                        ["None", "Large Font"],
                        ["None", "Colored"],
                        ["None", "Large Colored"],
                        ["None", "Large Bold"],
                        ["None", "Large Bold Italics Underlined"],
                    ]
                ],
                [],
            ],
            [
                [[["None", "Nested"]], [["None", "Table"]]],
                [[["None", "A"]], [["None", "B"]]],
            ],
            [
                [[["None"]]],
                [[["None", "Tab", "\t", "delimited", "\t", "text"]]],
                [[["None", "10 < 20 and 20 > 10"]]],
            ],
            [
                [
                    [
                        ["None", "Text outside table"],
                        ["None", "Reference footnote 1", "----footnote1----"],
                        ["None", "Reference footnote 2", "----footnote2----"],
                        ["None", "Reference endnote 1", "----endnote1----"],
                        ["None", "Reference endnote 2", "----endnote2----"],
                        ["Heading1", "Heading 1"],
                        ["Heading2", "Heading 2"],
                        ["None"],
                        ["None",
                         "----Image alt text---->A jellyfish in water\n\nDescription automatically generated<",
                         "----media/image2.jpg----"],
                    ]
                ]
            ],
            [[[["Footer"]]]],
            [[[["Footer",
                "Footer text",
                "----Image alt text---->A close up of a logo\n\nDescription automatically generated<",
                "----media/image1.png----"]]]],
            [[[["Footer"]]]],
            [
                [
                    [["None"]],
                    [["None"]],
                    [["FootnoteText", "footnote1)\t", " First footnote"]],
                    [
                        [
                            "FootnoteText",
                            "footnote2)\t",
                            " Second footnote",
                            "----Image alt text---->A close up of a logo\n\nDescription automatically generated<",
                            "----media/image1.png----",
                        ]
                    ],
                ]
            ],
            [
                [
                    [["None"]],
                    [["None"]],
                    [["EndnoteText", "endnote1)\t", " First endnote"]],
                    [
                        [
                            "EndnoteText",
                            "endnote2)\t",
                            " Second endnote",
                            "----Image alt text---->A close up of a logo\n\nDescription automatically generated<",
                            "----media/image1.png----",
                        ]
                    ],
                ]
            ],
        ]
        content.close()
