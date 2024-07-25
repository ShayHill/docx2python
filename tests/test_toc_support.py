""" Testing Table of Contents support as requested by user leboni

:author: Shay Hill
:created: 8/19/2020

User leboni forwarded a docx file, `zen_of_python.docx` with Table of Contents.
Addressing issue

`KeyError: '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'`

When attempting to extract content from such documents.

Two types of links in docx files. Internal links look like actual hyperlinks without
an href.

    <w:hyperlink w:anchor="_Toc48296956" w:history="1">
        <w:r w:rsidRPr="00810578">
            <w:rPr>
                <w:rStyle w:val="Hyperlink"/>
                <w:noProof/>
            </w:rPr>
            <w:t>Beautiful is better than ugly.</w:t>
        </w:r>
    </w:hyperlink>
"""

from paragraphs import par

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestTocText:
    def test_get_toc_text(self) -> None:
        """Extract header text from table-of-contents header."""
        extraction = docx2python(RESOURCES / "zen_of_python.docx")
        assert extraction.document_runs == [
            [
                [[["Contents"], ["\t", "Beautiful is better than ugly.\t1"], []]],
                [
                    [
                        [],
                        [],
                        ["Beautiful is better than ugly."],
                        ["Explicit is better than implicit."],
                        ["Simple is better than complex."],
                        ["Complex is better than complicated."],
                        ["Flat is better than nested."],
                        ["Sparse is better than dense."],
                        ["Readability counts."],
                        ["Special cases aren't special enough to break the rules."],
                        ["Although practicality beats purity."],
                        ["Errors should never pass silently."],
                        ["Unless explicitly silenced."],
                        ["In the face of ambiguity, refuse the temptation to guess."],
                        [
                            par(
                                """There should be one-- and preferably only one
                                --obvious way to do it."""
                            )
                        ],
                        [
                            par(
                                """Although that way may not be obvious at first
                                unless you're Dutch."""
                            )
                        ],
                        ["Now is better than never."],
                        ["Although never is often better than *right* now."],
                        ["If the implementation is hard to explain, it's a bad idea."],
                        [
                            par(
                                """If the implementation is easy to explain, it may
                                be a good idea."""
                            )
                        ],
                        [
                            par(
                                """Namespaces are one honking great idea -- let's do
                                more of those!"""
                            )
                        ],
                    ]
                ],
            ]
        ]
        extraction.close()
