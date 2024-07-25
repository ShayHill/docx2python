"""Pull some information from equations

:author: Shay Hill
:created: 7/7/2021

User sreeroopnaidu requested equation export. Equations are made up internally of
<w:m> elements. Previous versions of Docx2Python ignored these elements. These are
now recognized.

Equations in Word's Professional format will return garbage.
Equations in Word's Inline format will return a nice string.
"""

from docx2python import docx2python
from tests.conftest import RESOURCES


class TestEquations:
    def test_professional_format(self):
        """
        Start a new paragraph when a <w:br/> element is found.
        """
        with docx2python(RESOURCES / "equations.docx") as content:
            body = content.body
        assert body == [
            [
                [
                    [
                        "Professional Format",
                        "<latex>01x</latex>",
                        "Linear Format",
                        "<latex>\\int_{0}^{1}x</latex>",
                        "Linear Format with lt",
                        "<latex>\\int0<1x<5</latex>",
                    ]
                ]
            ]
        ]
