"""Test functions in docx2python.get_text.py

author: Shay Hill
created: 5/20/2019

Does not test ``get_text``. ``get text`` is tested through source_old.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict

import pytest
from lxml import etree

from docx2python.bullets_and_numbering import BulletGenerator, _increment_list_counter

from .helpers.utils import valid_xml


class TestIncrementListCounter:
    """Test get_text.increment_list_counter"""

    def test_function(self) -> None:
        """Increments counter at ilvl, deletes deeper counters."""
        ilvl2count = {str(x): x for x in range(1, 6)}
        assert ilvl2count == {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
        _ = _increment_list_counter(ilvl2count, "2")
        assert ilvl2count == {"1": 1, "2": 3}


@pytest.fixture()
def numbered_paragraphs():
    """Seven numbered paragraphs, indented 0-6 ilvls."""
    paragraphs: list[str] = []
    for ilvl in range(7):
        paragraphs.append(
            "<w:p><w:pPr><w:numPr>"
            + '<w:ilvl w:val="'
            + str(ilvl)
            + '"/>'
            + '<w:numId w:val="1"/>'
            + "</w:numPr></w:pPr></w:p>"
        )
    return [valid_xml(x) for x in paragraphs]


@pytest.fixture()
def numbering_context() -> dict[str, dict[str, str]]:
    """

    :return:
    """
    numId2numFmts = {
        "1": [
            "bullet",
            "decimal",
            "lowerLetter",
            "upperLetter",
            "lowerRoman",
            "upperRoman",
            "undefined",
        ]
    }
    numId2count = defaultdict(lambda: defaultdict(int))
    return {"numId2numFmts": numId2numFmts, "numId2count": numId2count}


class TestGetBulletString:
    """Test strip_test.get_bullet_string"""

    def test_bullet(self, numbered_paragraphs, numbering_context) -> None:
        """Returns '-- ' for 'bullet'"""

        paragraph = etree.fromstring(numbered_paragraphs[0])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == "--\t"

    def test_decimal(self, numbered_paragraphs, numbering_context) -> None:
        """
        Returns '1) ' for 'decimal'
        indented one tab
        """
        paragraph = etree.fromstring(numbered_paragraphs[1])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == "\t1)\t"

    def test_lower_letter(self, numbered_paragraphs, numbering_context) -> None:
        """
        Returns 'a) ' for 'lowerLetter'
        indented two tabs
        """
        paragraph = etree.fromstring(numbered_paragraphs[2])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == "\t\ta)\t"

    def test_upper_letter(self, numbered_paragraphs, numbering_context) -> None:
        """
        Returns 'A) ' for 'upperLetter'
        indented three tabs
        """
        paragraph = etree.fromstring(numbered_paragraphs[3])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == "\t\t\tA)\t"

    def test_lower_roman(self, numbered_paragraphs, numbering_context) -> None:
        """
        Returns 'i) ' for 'lowerRoman'
        indented 4 tabs
        """
        paragraph = etree.fromstring(numbered_paragraphs[4])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == "\t\t\t\ti)\t"

    def test_upper_roman(self, numbered_paragraphs, numbering_context) -> None:
        """
        Returns 'I) ' for 'upperRoman'
        indented 5 tabs
        """
        paragraph = etree.fromstring(numbered_paragraphs[5])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == "\t\t\t\t\tI)\t"

    def test_undefined(self, numbered_paragraphs, numbering_context) -> None:
        """
        Returns '-- ' for unknown formats
        indented 6 tabs

        Format "undefined" won't be defined in the function, so function will fall back
        to bullet string (with a warning).
        """
        paragraph = etree.fromstring(numbered_paragraphs[6])[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        with pytest.warns(UserWarning):
            _ = bullets.get_bullet(paragraph)

    def test_not_numbered(self, numbering_context) -> None:
        """
        Returns '' when paragraph is not numbered.
        """
        one_par_file = valid_xml("<w:p></w:p>")
        paragraph = etree.fromstring(one_par_file)[0]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        assert bullets.get_bullet(paragraph) == ""

    def test_resets_sublists(self, numbered_paragraphs, numbering_context):
        """Numbers reset when returning to shallower level

        1)  top level
            a)  level 2
            b)  another level 2
                A)  level 3
            c)  level 2 is still counting
                A)  NEW sublist of level 2
        2)  top level is still counting
            a)  NEW sublist of top level
        """
        pars = [numbered_paragraphs[x] for x in (1, 2, 2, 3, 2, 3, 1, 2)]
        bullets = BulletGenerator(numbering_context["numId2numFmts"])
        bullet_strings = []
        for par in pars:
            paragraph = etree.fromstring(par)[0]
            bullet_strings.append(bullets.get_bullet(paragraph).strip())

        assert bullet_strings == ["1)", "a)", "b)", "A)", "c)", "A)", "2)", "a)"]
