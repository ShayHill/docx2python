#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Form checkboxes, dropdowns, and other non-text elements visible in Word.

:author: Shay Hill
:created: 6/17/2020

Word represents some special characters as non-text elements (e.g., checkBox). These
functions examine these elements to infer suitable text replacements.

This file references "\u2610" and "\u2612" a few times. These are open and
crossed-out checkboxes. Pypi doesn't like them in my file, so I have to reference
them by their escape sequences.
"""

from typing import Union

from lxml import etree

from .namespace import qn


# noinspection PyPep8Naming
def get_checkBox_entry(checkBox: etree._Element) -> str:
    """Create text representation for a checkBox element.

    :param checkBox: a checkBox xml element
    :returns:
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

    def get_wval() -> Union[str, None]:
        checked = checkBox.find(qn("w:checked"))
        if checked is not None:
            return str(checked.attrib.get(qn("w:val"), "1"))
        default = checkBox.find(qn("w:default"))
        if default is not None:
            return str(default.attrib.get(qn("w:val"), "1"))
        return None

    return {"0": "\u2610", "1": "\u2612", None: "----checkbox failed----"}[get_wval()]


# noinspection PyPep8Naming
def get_ddList_entry(ddList: etree._Element) -> str:
    """Get only the selected string of a dropdown list.

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

    result = ddList.find(qn("w:result"))
    if result is None:
        list_index = 0
    else:
        try:
            list_index = int(str(result.attrib[qn("w:val")]))
        except (AttributeError, KeyError):
            list_index = 0
    return str(list_entries[list_index])
