#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Test that passing `more_html = True` collects paragraph styles

:author: Shay Hill
:created: 11/5/2020

Paragraphs and runs can end up nested with text boxes. Docx2python
un-nests these paragraphs.

	<w:p>
		<w:pPr>
			<w:pStyle w:val="Header"/>
		</w:pPr>
		<w:r>
                <w:t>EHS Manual</w:t>
		</w:r>
		<w:r>
			<w:p>
				<w:r>
					<w:t>EHS Manual</w:t>
				</w:r>
			</w:p>
			<w:p w14:paraId="37B5F1EE" w14:textId="1E56D065" w:rsidR="003A2388" w:rsidRPr="00815EC1" w:rsidRDefault="003A2388" w:rsidP="00CA47BD">
				<w:r>
					<w:t>EHS Manual</w:t>
				</w:r>
			</w:p>
		</w:r>
		<w:r>
			<w:t>EHS Manual</w:t>
		</w:r>
	</w:p>
```
    <open par 1>
        par 1 text
        <open par 2>
            par 2 text
        <close par 2>
        more par 1 text
    <close par 1>
```

gets flattened to

```
'par 1 text`
`par 2 text`
`more par 1 text`
```

In the output, this will look like three paragraphs. To keep things self-contained,
open/close html tags at the beginning and end of each *output* paragraph.

<w:p>
	<w:pPr>
		<w:pStyle w:val="Header"/>
	</w:pPr>
	<w:r w:rsidRPr="00210F67">
		<w:rPr>
			<w:sz w:val="17"/>
			<w:szCs w:val="17"/>
		</w:rPr>
		<w:p>
			<w:r>
				<w:rPr>
					<w:smallCaps/>
					<w:sz w:val="72"/>
					<w:szCs w:val="72"/>
				</w:rPr>
				<w:t>EHS Manual </w:t>
			</w:r>
		</w:p>
	</w:r>
	<w:r>
		<w:rPr>
			<w:noProof/>
		</w:rPr>
	</w:r>
</w:p>

"""

from docx2python.main import docx2python


def test_paragraphs_only() -> None:
    """Html tags inserted into text"""
    pars = docx2python(
        "resources/nested_paragraphs_in_header3b.docx",
        html=True,
        paragraph_styles=True,
    )
    assert pars.text == (
        "Header\n\nHeading1<h1>before nested "
        "paragraph----media/image19.jpeg----</h1>\n\n<span "
        'style="font-size:72pt;font-variant:small-caps">NESTED PARAGRAPH\n</span>'
        '\n\n<span style="font-size:72pt;font-variant:small-caps">Back to outside '
        "paragraph\n</span>\n\n----media/image20.png----\n\n\n\n2  "
        "\n\n\n\nNoSpacing\n\n\n\n\n\n\n\n\t\t<span "
        'style="color:808080;font-size:18pt">Page 579 of 579</span>'
        "\n\n\t\n\nFooter\t\t\t\t\n\n\n\n\n\n\n\n"
    )


class TestParsNestedInTables:
    """ Close html and paragraph tags when paragraphs are nested """

    def test_paragraphs_only(self) -> None:
        """Run without issue"""
        pars = docx2python(
            "resources/nested_paragraphs_in_header3b.docx",
            html=True,
            paragraph_styles=True,
        )
        assert pars.document_runs == [
            [[[["Header"]]]],
            [
                [
                    [
                        [
                            "Heading1",
                            "<h1>",
                            "before nested paragraph",
                            "----media/image19.jpeg----",
                            "</h1>",
                        ]
                    ]
                ]
            ],
            [
                [
                    [
                        [
                            "",
                            '<span style="font-size:72pt;font-variant:small-caps">NESTED PARAGRAPH\n</span>',
                        ]
                    ]
                ]
            ],
            [
                [
                    [
                        [
                            "",
                            '<span style="font-size:72pt;font-variant:small-caps">Back to outside paragraph\n</span>',
                        ]
                    ]
                ]
            ],
            [[[["----media/image20.png----"]]]],
            [[[[""], ["", "2 ", " "], [""], ["NoSpacing"], [""], [""], [""]]]],
            [
                [
                    [
                        [
                            "",
                            "\t",
                            "\t",
                            '<span style="color:808080;font-size:18pt">Page 579 of 579</span>',
                        ],
                        ["", "\t"],
                    ]
                ]
            ],
            [[[["Footer", "\t", "\t", "\t", "\t"]]]],
            [[[[""]], [[""]]]],
            [[[[""]], [[""]]]],
        ]


class TestBulletedLists:
    """Replace numbering format with bullet (--) when format cannot be determined"""

    def test_bulleted_lists(self) -> None:
        pars = docx2python("resources/created-in-pages-bulleted-lists.docx")
        assert pars.text == (
            "\n\nThis is a document for testing docx2python module.\n\n\n\n--\tWhy "
            "did the chicken cross the road?\n\n\t--\tJust because\n\n\t--\tDon't "
            "know\n\n\t--\tTo get to the other side\n\n--\tWhat's the meaning of life, "
            "universe and everything?\n\n\t--\t42\n\n\t--\t0\n\n\t--\t-1\n\n"
        )
