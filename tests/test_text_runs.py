"""Test functions in docx2python.text_runs.py

:author: Shay Hill
:created: 7/4/2019
"""

from lxml import etree

from docx2python.attribute_register import XML2HTML_FORMATTER
from docx2python.text_runs import gather_Pr, get_run_formatting, html_close, html_open
from tests.helpers.utils import valid_xml

ONE_TEXT_RUN = valid_xml(
    '<w:r w:rsidRPr="000E1B98">'
    + "<w:rPr>"
    + '<w:rFonts w:ascii="Arial"/>'
    + "<w:b/>"
    + "<w:u/>"
    + "<w:i/>"
    + '<w:sz w:val="32"/>'
    + '<w:color w:val="red"/>'
    + '<w:szCs w:val="32"/>'
    + '<w:u w:val="single"/>'
    + "</w:rPr>"
    + "<w:t>text styled  with rPr"
    + "</w:t>"
    + "</w:r>"
)

NO_STYLE_RUN = valid_xml(
    '<w:r w:rsidRPr="000E1B98">' + "<w:t>no styles applies" + "</w:t>" + "</w:r>"
)


class TestGatherRpr:
    """Test text_runs.gather_rPr"""

    def test_get_styles(self):
        """Map styles to values."""
        document = etree.fromstring(ONE_TEXT_RUN)
        assert gather_Pr(document[0][0][0]) == {
            "rFonts": None,
            "b": None,
            "u": "single",
            "i": None,
            "sz": "32",
            "color": "red",
            "szCs": "32",
        }

    def test_no_styles(self):
        """Return empty dict when no rPr for text run."""
        document = etree.fromstring(NO_STYLE_RUN)
        assert gather_Pr(document[0][0][0]) == {}


class TestGetRunStyle:
    """Test text_runs.get_run_style"""

    def test_font_and_others(self) -> None:
        """Return font first, then other styles."""
        document = etree.fromstring(ONE_TEXT_RUN)
        assert get_run_formatting(document[0][0][0], XML2HTML_FORMATTER) == [
            'span style="color:red;font-size:32pt"',
            "b",
            "i",
            "u",
        ]


class TestStyleStrings:
    """Test text_runs.style_open and text_runs.style_close"""

    def test_style_open(self) -> None:
        """Produce valid html for all defined styles."""
        style = ['span style="color:red"', "b", "i", "u"]
        assert html_open(style) == '<span style="color:red"><b><i><u>'

    def test_style_close(self) -> None:
        """Produce valid html for all defined styles."""
        style = ['span style="color:red"', "b", "i", "u"]
        assert html_close(style) == "</u></i></b></span>"
