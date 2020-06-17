#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Form checkboxes and dropdowns.

:author: Shay Hill
:created: 6/17/2020

There are two types of checkboxes in Word

This file references "\u2610" and "\u2612" a few times. These are open and
crossed-out checkboxes. Pypi doesn't like them in my file, so I have to reference
them by their escape sequences.
"""

from contextlib import suppress
from typing import Union
from xml.etree.ElementTree import Element

from .namespace import qn


# noinspection PyPep8Naming
def get_checkBox_entry(checkBox: Element) -> str:
    """
    Create text representation for a checkBox element.

    :param checkBox: a checkBox xml element
    :returns:
        1. attempt to get checked.w:val and return "\u2610" or "\u2612"
        2. attempt to get default.w:val and return "\u2610" or "\u2612"
        3. return ``--checkbox failed--``

    checkBox can only be checked when the form is locked. Does not print text.
    checkbox can be checked any time. Prints text as "\u2610" or "\u2612".

    <w:checkBox>
        <w:sizeAuto/>
        <w:default w:val="1"/>
        <w:checked w:val="0"/>
    </w:checkBox>

    The ``checked`` value might be absent or blank if the selected value matches the
    default.
    """

    def get_wval() -> Union[str, None]:
        with suppress(AttributeError, KeyError):
            return checkBox.find(qn("w:checked")).attrib[qn("w:val")]
        with suppress(AttributeError, KeyError):
            return checkBox.find(qn("w:default")).attrib[qn("w:val")]

    return {"0": "\u2610", "1": "\u2612", None: "----checkbox failed----"}[get_wval()]


# noinspection PyPep8Naming
def get_ddList_entry(ddList: Element) -> str:
    """
    Get only the selected string of a dropdown list.

    <w:ddList>
        <w:result w:val="1"/>
        <w:listEntry w:val="selection 1"/>
        <w:listEntry w:val="selection 2"/>
    </w:ddList>

    <w:result w:val="0"/> might be missing when selection is "0"
    """

    list_entries = [
        x.attrib.get(qn("w:val")) for x in ddList.findall(qn("w:listEntry"))
    ]
    try:
        list_index = int(ddList.find(qn("w:result")).attrib.get(qn("w:val"), 0))
    except AttributeError:
        list_index = 0
    return list_entries[list_index]
