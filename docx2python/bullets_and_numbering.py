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
from typing import Callable

from lxml.etree import _Element as EtreeElement  # type: ignore

from docx2python import numbering_formats as nums
from docx2python.namespace import qn


def _get_bullet_function(numFmt: str) -> Callable[[int], str]:
    """Select a bullet or numbering format function from xml numFmt.

    :param numFmt: xml numFmt (e.g., decimal, lowerLetter)
    :return: a function that takes an int and returns a string. If numFmt is not
        recognized, treat numbers as bullets.
    """
    numFmt2bullet_function: dict[str, Callable[[int], str]] = {
        "decimal": nums.decimal,
        "lowerLetter": nums.lower_letter,
        "upperLetter": nums.upper_letter,
        "lowerRoman": nums.lower_roman,
        "upperRoman": nums.upper_roman,
        "bullet": nums.bullet,
    }
    try:
        retval_: Callable[[int], str] = numFmt2bullet_function[numFmt]
        return retval_
    except KeyError:
        warnings.warn(
            f"{numFmt} numbering format not implemented, "
            + f"substituting '{nums.bullet()}'"
        )
        return nums.bullet


def _new_list_counter() -> defaultdict[str, defaultdict[str, int]]:
    """
    A counter, starting at zero, for each numId

    :return: {
        a_numId: 0,
        b_numId: 0
    }

    This is what you need to keep track of where every nested list is at.
    """
    return defaultdict(lambda: defaultdict(lambda: 0))


def _increment_list_counter(ilvl2count: defaultdict[str, int], ilvl: str) -> int:
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

    def __init__(self, numId2numFmts: dict[str, list[str]]) -> None:
        """
        Set numId2numFmts. Initiate counters.
        """
        self.numId2numFmts = numId2numFmts
        self.numId2count = _new_list_counter()

    def get_bullet(self, paragraph: EtreeElement) -> str:
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
            pPr = next(paragraph.iterfind(qn("w:pPr")))
            numPr = next(pPr.iterfind(qn("w:numPr")))
            numId = next(numPr.iterfind(qn("w:numId"))).attrib[qn("w:val")]
            ilvl = next(numPr.iterfind(qn("w:ilvl"))).attrib[qn("w:val")]
            try:
                numFmt = self.numId2numFmts[str(numId)][int(ilvl)]
            except IndexError:
                # give up and put a bullet
                numFmt = "bullet"
        except (StopIteration, KeyError):
            # not a numbered paragraph
            return ""

        def format_bullet(bullet: str) -> str:
            """Indent, format and pad the bullet or number string.

            :param bullet: any kind of list-item string (bullet, number, Roman, ...)
            :return: formatted bullet string
            """
            if bullet != nums.bullet():
                bullet += ")"
            return "\t" * int(ilvl) + bullet + "\t"

        number = _increment_list_counter(self.numId2count[numId], str(ilvl))
        get_unformatted_bullet_str = _get_bullet_function(numFmt)
        return format_bullet(get_unformatted_bullet_str(number))
