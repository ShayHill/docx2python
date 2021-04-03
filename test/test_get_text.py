#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test functions in docx2python.get_text.py

author: Shay Hill
created: 5/20/2019

Does not test ``get_text``. ``get text`` is tested through source_old.
"""


from collections import defaultdict
from typing import Any, Dict, List
from dataclasses import dataclass
from docx2python.docx_organization import File, DocxContext

from functools import cached_property
from pytest_mock import mocker
import pytest
from xml.etree import ElementTree

import pytest
from unittest.mock import PropertyMock


# noinspection PyUnresolvedReferences
from helpers.utils import valid_xml

# noinspection PyProtectedMember,PyProtectedMember
from docx2python.docx_text import _get_bullet_string, _increment_list_counter


class TestIncrementListCounter:
    """Test get_text.increment_list_counter """

    def test_function(self) -> None:
        """Increments counter at ilvl, deletes deeper counters."""
        ilvl2count = {str(x): x for x in range(1, 6)}
        assert ilvl2count == {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
        _increment_list_counter(ilvl2count, "2")
        assert ilvl2count == {"1": 1, "2": 3}


@pytest.fixture()
def context_dict() -> Dict[str, Any]:
    """Simulate context dictionary for tests."""
    return {
        "numId2numFmts": {
            "1": [
                "bullet",
                "decimal",
                "lowerLetter",
                "upperLetter",
                "lowerRoman",
                "upperRoman",
                "undefined",
            ]
        },
        "numId2count": {"1": defaultdict(lambda: 0)},
    }


@dataclass
class MockFile:
    def __init__(self):
        self.numId2numFmts = {
            "numId2numFmts": {
                "1": [
                    "bullet",
                    "decimal",
                    "lowerLetter",
                    "upperLetter",
                    "lowerRoman",
                    "upperRoman",
                    "undefined",
                ]
            },
            "numId2count": {"1": defaultdict(lambda: 0)},
        }


@pytest.fixture()
def numbered_paragraphs():
    """Seven numbered paragraphs, indented 0-6 ilvls."""
    paragraphs = []
    for ilvl in range(7):
        paragraphs.append(
            "<w:p><w:pPr><w:numPr>"
            '<w:ilvl w:val="' + str(ilvl) + '"/>'
            '<w:numId w:val="1"/>'
            "</w:numPr></w:pPr></w:p>"
        )
    return [valid_xml(x) for x in paragraphs]


class MockContentClassWithNumbering(DocxContext):
    """
    DocxContent substitute with explicated numId2numFmts and numId2count
    """

    @cached_property
    def numId2numFmts(self):
        return {
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

    @cached_property
    def numId2count(self):
        return {"1": defaultdict(lambda: 0)}


class MockContentClassWithoutNumbering(DocxContext):
    """
    DocxContent substitute with missing numId2numFmts and numId2count
    """

    pass


@pytest.fixture()
def file_with_numbering() -> File:
    """
    File with a simulated context (from which numbering information may be supplied)
    """
    return File(
        MockContentClassWithNumbering("bs_filename"),
        {"Id": "bs", "Type": "bs", "Target": "bs", "dir": "bs"},
    )


@pytest.fixture()
def file_without_numbering() -> File:
    """
    File with a simulated context (from which numbering information will be missing)
    """
    return File(
        MockContentClassWithoutNumbering("bs_filename"),
        {"Id": "bs", "Type": "bs", "Target": "bs", "dir": "bs"},
    )


class TestGetBulletString:
    """Test strip_test.get_bullet_string """

    def test_bullet(self, numbered_paragraphs, file_with_numbering) -> None:
        """Returns '-- ' for 'bullet'"""

        assert file_with_numbering.context.numId2numFmts["1"][0] == "bullet"
        paragraph = ElementTree.fromstring(numbered_paragraphs[0])[0]
        assert _get_bullet_string(file_with_numbering, paragraph) == "--\t"

    def test_decimal(self, numbered_paragraphs, file_with_numbering) -> None:
        """
        Returns '1) ' for 'decimal'
        indented one tab
        """
        assert file_with_numbering.context.numId2numFmts["1"][1] == "decimal"
        paragraph = ElementTree.fromstring(numbered_paragraphs[1])[0]
        assert _get_bullet_string(file_with_numbering, paragraph) == "\t1)\t"

    def test_lower_letter(self, numbered_paragraphs, file_with_numbering) -> None:
        """
        Returns 'a) ' for 'lowerLetter'
        indented two tabs
        """
        assert file_with_numbering.context.numId2numFmts["1"][2] == "lowerLetter"
        paragraph = ElementTree.fromstring(numbered_paragraphs[2])[0]
        assert _get_bullet_string(file_with_numbering, paragraph) == "\t\ta)\t"

    def test_upper_letter(self, numbered_paragraphs, file_with_numbering) -> None:
        """
        Returns 'A) ' for 'upperLetter'
        indented three tabs
        """
        assert file_with_numbering.context.numId2numFmts["1"][3] == "upperLetter"
        paragraph = ElementTree.fromstring(numbered_paragraphs[3])[0]
        assert _get_bullet_string(file_with_numbering, paragraph) == "\t\t\tA)\t"

    def test_lower_roman(self, numbered_paragraphs, file_with_numbering) -> None:
        """
        Returns 'i) ' for 'lowerRoman'
        indented 4 tabs
        """
        assert file_with_numbering.context.numId2numFmts["1"][4] == "lowerRoman"
        paragraph = ElementTree.fromstring(numbered_paragraphs[4])[0]
        assert _get_bullet_string(file_with_numbering, paragraph) == "\t\t\t\ti)\t"

    def test_upper_roman(self, numbered_paragraphs, file_with_numbering) -> None:
        """
        Returns 'I) ' for 'upperRoman'
        indented 5 tabs
        """
        assert file_with_numbering.context.numId2numFmts["1"][5] == "upperRoman"
        paragraph = ElementTree.fromstring(numbered_paragraphs[5])[0]
        assert _get_bullet_string(file_with_numbering, paragraph) == "\t\t\t\t\tI)\t"

    def test_undefined(self, numbered_paragraphs, file_with_numbering) -> None:
        """
        Returns '-- ' for unknown formats
        indented 6 tabs

        Format "undefined" won't be defined in the function, so function will fall back
        to bullet string (with a warning).
        """
        assert file_with_numbering.context.numId2numFmts["1"][6] == "undefined"
        paragraph = ElementTree.fromstring(numbered_paragraphs[6])[0]
        with pytest.warns(UserWarning):
            assert (
                _get_bullet_string(file_with_numbering, paragraph) == "\t\t\t\t\t\t--\t"
            )

    def test_not_numbered(self, file_without_numbering) -> None:
        """
        Returns '' when paragraph is not numbered.
        """
        one_par_file = valid_xml("<w:p></w:p>")
        paragraph = ElementTree.fromstring(one_par_file)[0]
        assert _get_bullet_string(file_without_numbering, paragraph) == ""

    def test_resets_sublists(self, numbered_paragraphs, file_with_numbering):
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
        bullets = []
        for par in pars:
            paragraph = ElementTree.fromstring(par)[0]
            bullets.append(_get_bullet_string(file_with_numbering, paragraph).strip())
        assert bullets == ["1)", "a)", "b)", "A)", "c)", "A)", "2)", "a)"]
