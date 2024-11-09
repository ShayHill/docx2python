"""Generate bullet and numbered-list strings.

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
from contextlib import suppress
from typing import TYPE_CHECKING, Callable

from docx2python import numbering_formats as nums
from docx2python.namespace import get_attrib_by_qn, iterfind_by_qn

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from docx2python.docx_context import NumIdAttrs


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
    except KeyError:
        warnings.warn(
            f"{numFmt} numbering format not implemented, "
            + f"substituting '{nums.bullet()}'",
            stacklevel=2,
        )
        return nums.bullet
    else:
        return retval_


def _new_list_counter() -> defaultdict[str, defaultdict[str, int]]:
    """Return a counter, starting at zero, for each numId.

    :return: {
        a_numId: 0,
        b_numId: 0
    }

    This is what you need to keep track of where every nested list is at.
    """
    return defaultdict(lambda: defaultdict(int))


def _increment_list_counter(ilvl2count: defaultdict[str, int], ilvl: str) -> int:
    """Increase counter at ilvl, reset counter at deeper levels.

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
    deeper_levels = [k for k in ilvl2count if k > ilvl]
    for level in deeper_levels:
        del ilvl2count[level]
    return ilvl2count[ilvl]


class BulletGenerator:
    """Keep track of list counters and generate bullet strings.

    <w:p>
        <w:pPr>
            <w:numPr>
                <w:ilvl w:val="0"/>   # indentation level
                <w:numId w:val="9"/>  # index to (multi-level) list format
            </w:numPr>
        </wpPr>
        <w:r>
            <w:t>this text in numbered or bulleted list
            </w:t>
        </w:r>
    </w:p>
    """

    def __init__(self, numId2Attrs: dict[str, list[NumIdAttrs]]) -> None:
        """Set numId2numFmts. Initiate counters."""
        self.numId2Attrs = numId2Attrs
        self.numId2count = _new_list_counter()

        # Only increment the number of a paragraph if that paragraph has not been
        # seen. See docstring for self._get_par_number.
        self._par2par_number: dict[EtreeElement, int | None] = {}

    def _get_numPr(self, paragraph: EtreeElement) -> EtreeElement | None:
        """Get the parent element of the numId and ilvl elements.

        :param paragraph: <w:p> xml element
        :return: <w:numPr> xml element or None if this fails.
        """
        try:
            pPr = next(iterfind_by_qn(paragraph, "w:pPr"))
            return next(iterfind_by_qn(pPr, "w:numPr"))
        except (StopIteration, KeyError):
            return None

    def _get_numId(self, numPr: EtreeElement) -> str | None:
        """Get the numId for the paragraph.

        :param numPr: <w:numPr> xml element (see class docstring)
        :return: numId as a string or None if this fails.

        The numId is an integer (string of an integer) index to a list of multi-level
        list formats. For each numId, there is a list of formats for each indentation
        level.
        """
        try:
            numId_element = next(iterfind_by_qn(numPr, "w:numId"))
            return get_attrib_by_qn(numId_element, "w:val")
        except (StopIteration, KeyError):
            return None

    def _get_ilvl(self, numPr: EtreeElement) -> str | None:
        """Get the ilvl for the paragraph.

        :param numPr: <w:numPr> xml element (see class docstring)
        :return: ilvl as a string or None if this fails.

        The ilvl is an integer (string of an integer) index of a multi-level list
        formats. For each ilvl, there is a format.
        """
        try:
            ilvl_element = next(iterfind_by_qn(numPr, "w:ilvl"))
            return get_attrib_by_qn(ilvl_element, "w:val")
        except (StopIteration, KeyError):
            return None

    def get_bullet_fmt(self, paragraph: EtreeElement) -> tuple[str | None, str | None]:
        """Expose the numId and ilvl of a numbered paragraph.

        :param paragraph: <w:p> xml element
        :return: numId (which list), ilvl (indentation level)

        This will return None, None, None if the paragraph is not numbered.
        """
        numPr = self._get_numPr(paragraph)
        if numPr is None:
            return None, None
        numId = self._get_numId(numPr)
        ilvl = self._get_ilvl(numPr)
        if numId is None or ilvl is None:
            return numId, ilvl
        return numId, ilvl

    def get_par_number(self, paragraph: EtreeElement) -> int | None:
        """Get the number (at the current indentation level) of a paragraph.

        :param paragraph: <w:p> xml element
        :return: number of the paragraph
        :effects: increment self.numId2count[numId][ilvl] if the paragraph has not
            been seen before.

        E.g.,

            1. paragraph  # called here, return 1
                a. paragraph  # called here, return 1
                b. paragraph  # called here, return 2
            2. paragraph  # called here, return 2
                a. paragraph  # called here, return 1
                    1. paragraph  # called here, return 1

        numId and ilvl should both be defined for a numbered paragraph, but I'm
        testing both here to fail silently if that assumption is wrong.
        """
        with suppress(KeyError):
            return self._par2par_number[paragraph]
        numId, ilvl = self.get_bullet_fmt(paragraph)
        if numId is None or ilvl is None:
            par_number = None
        else:
            counter = _increment_list_counter(self.numId2count[numId], ilvl)
            par_number = counter + self.get_start_value_zero_based(numId, ilvl)
        self._par2par_number[paragraph] = par_number
        return par_number

    def get_start_value_zero_based(self, numId: str | None, ilvl: str | None) -> int:
        """Get the start value, 0-based, for numbering sequence at particular level.

        :return: start index if present for a particular numId and ilvl, 0 otherwise
        """
        attrs = self.__get_num_fmt_attributes(numId, ilvl)
        if not attrs or not attrs.start:
            return 0
        return attrs.start - 1  # subtract 1 to have 0-based result

    def get_list_position(
        self, paragraph: EtreeElement
    ) -> tuple[str | None, list[int]]:
        """Get the current numbering values.

        :return: numbering values as a tuple of integers

        E.g.,

            Not in a list  # called here, return ()

            1. paragraph  # called here, return (numPr, 1)
                a. paragraph  # called here, return (numPr, 1, 1)
                b. paragraph  # called here, return (numPr, 1, 2)
            2. paragraph  # called here, return (numPr, 2)
                a. paragraph  # called here, return (numPr, 2, 1)
                    1. paragraph  # called here, return (numPr, 2, 1, 1)

        The numbering values are the current count at each indentation level.
        """
        numPr, _ = self.get_bullet_fmt(paragraph)
        if numPr is None:
            return (numPr, [])
        # ensure the paragraph counter has been incremented
        _ = self.get_par_number(paragraph)
        return numPr, list(self.numId2count[numPr].values())

    def get_bullet(self, paragraph: EtreeElement) -> str:
        """Get bullet string if paragraph is numbered. (e.g, '--  ' or '1)  ').

        :param paragraph: <w:p> xml element
        :return: specified 'bullet' string or '' if paragraph is not numbered

        Get an index to a multi-level list format (numId) and the indentation level
        (ilvl). If no numId or ilvl are defined, assume this is not a numbered list.
        If these values to exist, look up a list format with
        numId2numFmts[numId][ilvl]. If this fails, silently give up and use a bullet.

        bullet preceded by one tab for every indentation level.
        """
        numId, ilvl = self.get_bullet_fmt(paragraph)
        number = self.get_par_number(paragraph)
        if numId is None:
            return ""
        if ilvl is None:
            return ""
        if number is None:
            return ""
        attrs = self.__get_num_fmt_attributes(numId, ilvl)
        numFmt = attrs.fmt if attrs and attrs.fmt else "bullet"

        def format_bullet(bullet: str) -> str:
            """Indent, format and pad the bullet or number string.

            :param bullet: any kind of list-item string (bullet, number, Roman, ...)
            :return: formatted bullet string
            """
            if bullet != nums.bullet():
                bullet += ")"
            return "\t" * int(ilvl) + bullet + "\t"

        get_unformatted_bullet_str = _get_bullet_function(numFmt)
        return format_bullet(get_unformatted_bullet_str(number))

    def __get_num_fmt_attributes(
        self, numId: str | None, ilvl: str | None
    ) -> NumIdAttrs | None:
        if numId is None:
            return None
        if ilvl is None:
            return None
        try:
            return self.numId2Attrs[str(numId)][int(ilvl)]
        except (KeyError, IndexError, ValueError):
            return None
