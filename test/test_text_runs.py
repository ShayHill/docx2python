#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test functions in docx2python.text_runs.py

:author: Shay Hill
:created: 7/4/2019
"""

from xml.etree import ElementTree

# noinspection PyUnresolvedReferences
from helpers.utils import valid_xml

# noinspection PyProtectedMember
from docx2python.text_runs import (
    _elem_tag_str,
    gather_Pr,
    get_run_style,
    style_close,
    style_open,
)

ONE_TEXT_RUN = valid_xml(
    '<w:r w:rsidRPr="000E1B98">'
    "<w:rPr>"
    '<w:rFonts w:ascii="Arial"/>'
    "<w:b/>"
    "<w:u/>"
    "<w:i/>"
    '<w:sz w:val="32"/>'
    '<w:color w:val="red"/>'
    '<w:szCs w:val="32"/>'
    '<w:u w:val="single"/>'
    "</w:rPr>"
    "<w:t>text styled  with rPr"
    "</w:t>"
    "</w:r>"
)

NO_STYLE_RUN = valid_xml(
    '<w:r w:rsidRPr="000E1B98">' "<w:t>no styles applies" "</w:t>" "</w:r>"
)


class TestElemTagStr:
    """Test text_runs.elem_tag_str"""

    def test_get_tag(self) -> None:
        """Return everything after the colon."""
        document = ElementTree.fromstring(ONE_TEXT_RUN)
        assert _elem_tag_str(document) == "document"
        assert _elem_tag_str(document[0]) == "r"


class TestGatherRpr:
    """Test text_runs.gather_rPr """

    def test_get_styles(self):
        """Map styles to values."""
        document = ElementTree.fromstring(ONE_TEXT_RUN)
        assert gather_Pr(document[0]) == {
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
        document = ElementTree.fromstring(NO_STYLE_RUN)
        assert gather_Pr(document[0]) == {}


class TestGetRunStyle:
    """Test text_runs.get_run_style """

    def test_font_and_others(self) -> None:
        """Return font first, then other styles."""
        document = ElementTree.fromstring(ONE_TEXT_RUN)
        assert get_run_style(document[0]) == [
            ("font", 'color="red" size="32"'),
            ("b", ""),
            ("i", ""),
            ("u", ""),
        ]


class TestStyleStrings:
    """Test text_runs.style_open and text_runs.style_close """

    def test_style_open(self) -> None:
        """Produce valid html for all defined styles."""
        style = [("font", 'color="red" size="32"'), ("b", ""), ("i", ""), ("u", "")]
        assert style_open(style) == '<font color="red" size="32"><b><i><u>'

    def test_style_close(self) -> None:
        """Produce valid html for all defined styles."""
        style = [("font", 'color="red" size="32"'), ("b", ""), ("i", ""), ("u", "")]
        assert style_close(style) == "</u></i></b></font>"
