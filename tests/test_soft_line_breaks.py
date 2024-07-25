"""Start a new paragraph at a soft line break ``<w:br>``

:author: Shay Hill
:created: 7/7/2021

Docx2Python previously ignored <w:br/> elements:

    ```
    pars = docx2python('soft_line_breaks.docx')
    [[[[['Line1Line2Line3'], ['Line4'], []]], [[[]]]], [[[[]]]]]
    ```
"""

from docx2python import docx2python
from docx2python.iterators import iter_paragraphs
from tests.conftest import RESOURCES


class TestSoftLineBreaks:
    def test_separate_pars(self):
        """
        Start a new paragraph when a <w:br/> element is found.
        """
        with docx2python(RESOURCES / "soft_line_breaks.docx") as content:
            body = content.body
        pars = [x for x in iter_paragraphs(body) if x]
        assert pars == ["Line1\nLine2\nLine3", "Line4"]
