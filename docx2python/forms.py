"""Form checkboxes, dropdowns, and other non-text elements visible in Word.

:author: Shay Hill
:created: 6/17/2020

Word represents some special characters as non-text elements (e.g., checkBox). These
functions examine these elements to infer suitable text replacements.

This file references "\u2610" and "\u2612" a few times. These are open and
crossed-out checkboxes. Pypi doesn't like them in my file, so I have to reference
them by their escape sequences.
"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from docx2python.namespace import get_attrib_by_qn, iterfind_by_qn, qn

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore


def get_checkBox_entry(checkBox: EtreeElement) -> str:
    """Create text representation for a checkBox element.

    :param checkBox: a checkBox xml element
    :return:
        1. attempt to get ``checked.w:val`` and return "\u2610" or "\u2612"
        2. attempt to get ``default.w:val`` and return "\u2610" or "\u2612"
        3. return ``--checkbox failed--``

    Docx xml has at least two types of checkbox elements::

        1. ``checkBox`` can only be checked when the form is locked. These do not
        contain a text element, so this function is needed to select one from the
        ``w:checked`` or ``w:default`` sub-elements.

        2. ``checkbox`` can be checked any time. Prints text as "\u2610" or "\u2612".
        Docx2Python can safely ignore this second type, as there will be a <w:t>
        element inside with a checkbox character.

    <w:checkBox>
        <w:sizeAuto/>
        <w:default w:val="1"/>
        <w:checked w:val="0"/>
    </w:checkBox>

    If the ``checked`` attribute is absent, return the default
    If the ``checked`` attribute is present, but not w:val is given, return unchecked
    """

    def get_wval() -> str | None:
        """Get the value of the ``w:val`` attribute of the ``checked`` element.

        :return: the value of the ``w:val`` attribute of the ``checked`` element
        """
        with suppress(StopIteration):
            checked = next(iterfind_by_qn(checkBox, "w:checked"))
            return str(checked.attrib.get(qn(checked, "w:val")) or "1")
        with suppress(StopIteration, KeyError):
            default = next(iterfind_by_qn(checkBox, "w:default"))
            return str(get_attrib_by_qn(default, "w:val"))
        return None

    return {
        "0": "\u2610",
        "false": "\u2610",
        "1": "\u2612",
        "true": "\u2612",
        None: "----checkbox failed----",
    }[get_wval()]


def get_ddList_entry(ddList: EtreeElement) -> str:
    """Get only the selected string of a dropdown list.

    :param ddList: a dropdown-list element
    :return: w:listEntry value of input element.

    <w:ddList>
        <w:result w:val="1"/>
        <w:listEntry w:val="selection 1"/>
        <w:listEntry w:val="selection 2"/>
    </w:ddList>

    <w:result w:val="0"/> might be missing when selection is "0"
    """
    list_entries = [
        get_attrib_by_qn(x, "w:val") for x in iterfind_by_qn(ddList, "w:listEntry")
    ]
    try:
        result = next(iterfind_by_qn(ddList, "w:result"))
        list_index = int(get_attrib_by_qn(result, "w:val"))
    except (StopIteration, KeyError):
        list_index = 0
    return str(list_entries[list_index])
