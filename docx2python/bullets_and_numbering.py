#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Generate bullet and numbered-list strings.

:author: Shay Hill
:created: 11/15/2021

Docx xml files do not track explicit numbering values. Each numbered paragraph has ::

    <w:ilvl w:val="0"/>   # indentation level
    <w:numId w:val="9"/>  # index to a list [by ilvl] of numbered-list formats

Docx2Python keeps track of current numbering value, and increments these values as
numbered paragraphs are encountered. If extracting partial text, the numbers may be
incorrect, because all paragraphs in a numbered-list format may not be encountered
during the extraction.
"""
from __future__ import annotations

import warnings
from collections import defaultdict
from typing import Any, Dict, List, Callable

from lxml import etree

from docx2python import numbering_formats as nums
from docx2python.namespace import qn


# noinspection PyPep8Naming
def _get_bullet_function(numFmt: str) -> Callable[[int], str]:
    """
    Select a bullet or numbering type from xml numFmt.
    """
    numFmt2bullet_function = {
        "decimal": nums.decimal,
        "lowerLetter": nums.lower_letter,
        "upperLetter": nums.upper_letter,
        "lowerRoman": nums.lower_roman,
        "upperRoman": nums.upper_roman,
        "bullet": nums.bullet,
    }
    try:
        return numFmt2bullet_function[numFmt]
    except KeyError:
        warnings.warn(
            "{} numbering format not implemented, substituting '{}'".format(
                numFmt, nums.bullet()
            )
        )
        return nums.bullet


def _new_list_counter() -> defaultdict[Any, defaultdict[Any, 0]]:
    """
    A counter, starting at zero, for each numId

    :return: {
        a_numId: 0,
        b_numId: 0
    }

    This is what you need to keep track of where every nested list is at.
    """
    return defaultdict(lambda: defaultdict(lambda: 0))


def _increment_list_counter(ilvl2count, ilvl: str) -> int:
    # noinspection SpellCheckingInspection
    """
    Increase counter at ilvl, reset counter at deeper levels.

    :param ilvl2count: context['numId2count']
    :param ilvl: string representing an integer
    :return: updated count at ilvl.
        updates context['numId2count'] by reference

    On a numbered list, the count for sub-lists should reset when a parent list
    increases, e.g.,

    1. top-level list
        a. sublist
        b. sublist continues
    2. back to top-level list
        a. sublist counter has been reset

    List counters are defaultdicts, so we can reset sublist counters by deleting
    them.
    """
    ilvl2count[ilvl] += 1
    deeper_levels = [x for x in ilvl2count.keys() if x > ilvl]
    for level in deeper_levels:
        del ilvl2count[level]
    return ilvl2count[ilvl]


class BulletGenerator:
    """
    Keep track of list counters and generate bullet strings.
    """

    # noinspection PyPep8Naming
    def __init__(self, numId2numFmts: Dict[str, List[str]]) -> None:
        """
        Set numId2numFmts. Initiate counters.
        """
        self.numId2numFmts = numId2numFmts
        self.numId2count = _new_list_counter()

    # noinspection PyPep8Naming
    def get_bullet(self, paragraph: etree.Element) -> str:
        """
        Get bullet string if paragraph is numbered. (e.g, '--  ' or '1)  ')

        :param paragraph: <w:p> xml element
        :return: specified 'bullet' string or '' if paragraph is not numbered

        <w:p>
            <w:pPr>
                <w:numPr>
                    <w:ilvl w:val="0"/>
                    <w:numId w:val="9"/>
                </w:numPr>
            </wpPr>
            <w:r>
                <w:t>this text in numbered or bulleted list
                </w:t>
            </w:r>
        </w:p>

        bullet preceded by one tab for every indentation level.
        """
        try:
            pPr = paragraph.find(qn("w:pPr"))
            numPr = pPr.find(qn("w:numPr"))
            numId = numPr.find(qn("w:numId")).attrib[qn("w:val")]
            ilvl = numPr.find(qn("w:ilvl")).attrib[qn("w:val")]
            try:
                numFmt = self.numId2numFmts[numId][int(ilvl)]
            except IndexError:
                # give up and put a bullet
                numFmt = "bullet"
        except (AttributeError, KeyError):
            # not a numbered paragraph
            return ""

        def format_bullet(bullet: str) -> str:
            """Indent, format and pad the bullet or number string."""
            if bullet != nums.bullet():
                bullet += ")"
            return "\t" * int(ilvl) + bullet + "\t"

        number = _increment_list_counter(self.numId2count[numId], ilvl)
        get_unformatted_bullet_str = _get_bullet_function(numFmt)
        return format_bullet(get_unformatted_bullet_str(number))
