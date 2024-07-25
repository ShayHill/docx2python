""" Run styles converted to html

:author: Shay Hill
:created: 3/18/2021

<w:r><w:rPr><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t>16 point</w:t></w:r>
<w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t>Red</w:t></w:r>
<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>
    </w:rPr><w:t>Courier new</w:t></w:r>
<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>Italic</w:t></w:r>
<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Bold</w:t></w:r>
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>Underline</w:t></w:r>
<w:r><w:rPr><w:strike/></w:rPr><w:t>Strikethrough</w:t></w:r>
<w:r><w:rPr><w:dstrike/></w:rPr><w:t>Double Strikethrough</w:t></w:r>
<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>Superscript</w:t></w:r>
<w:r><w:rPr><w:vertAlign w:val="subscript"/></w:rPr><w:t>Subscript</w:t></w:r>
<w:r><w:rPr><w:smallCaps/></w:rPr><w:t>Small Caps</w:t></w:r>
<w:r><w:rPr><w:caps/></w:rPr><w:t>All Caps</w:t></w:r>
<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>Highlighted yellow</w:t></w:r>
<w:r><w:rPr><w:highlight w:val="green"/></w:rPr><w:t>Highlighted green</w:t></w:r>

<i> italic
<b> bold
<u> underline
<s> strike
<del> double strike
<sup> superscript
<sub> subscript
<font style="font-variant: small-caps">small caps
<font style="text-transform:uppercase">all caps
<span style="background-color: yellow">highlighted yellow
<span style="background-color: green">highlighted green
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestParStyles:
    def test_par_styles(self) -> None:
        """
        If do_html, paragraphs style is the first element of every run

        :return:
        """
        content = docx2python(RESOURCES / "run_styles.docx", html=True)
        assert content.document_runs == [
            [
                [
                    [
                        ["Normal"],
                        ['<span style="font-size:32pt">16 point</span>'],
                        ['<span style="color:FF0000">Red</span>'],
                        ["Courier new"],
                        ["<i>Italic</i>"],
                        ["<b>Bold</b>"],
                        ["<u>Underline</u>"],
                        ["<s>Strikethrough</s>"],
                        ["Double Strikethough"],
                        ["<sup>Superscript</sup>"],
                        ["<sub>Subscript</sub>"],
                        ['<span style="font-variant:small-caps">Small Caps</span>'],
                        ['<span style="text-transform:uppercase">All Caps</span>'],
                        [
                            '<span style="background-color:yellow">'
                            + "Highlighted yellow</span>"
                        ],
                        [
                            '<span style="background-color:green">'
                            + "Highlighted green</span>"
                        ],
                        ["<b>Consecutive</b>"],
                        ["<b>Bold</b>"],
                        ["<b>Paragraphs</b>"],
                        [
                            '<span style="font-size:24pt"><sub>Subscript </sub></span>',
                            '<span style="font-size:24pt;font-variant:small-caps">'
                            + "Small Caps </span>",
                            '<span style="font-size:24pt;text-transform:uppercase">'
                            + "All Caps </span>",
                            '<span style="background-color:yellow;font-size:24pt">'
                            + "Highlighted yellow </span>",
                            '<span style="background-color:green;font-size:24pt">'
                            + "Highlighted green</span>",
                        ],
                        [],
                        [],
                    ]
                ]
            ]
        ]
        content.close()
