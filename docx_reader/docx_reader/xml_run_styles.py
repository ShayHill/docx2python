#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" (exhaustive ?) set of run formatting tags

:author: Shay Hill
:created: 10/24/2021

A Word ``run`` element will (always?) have a child ``rPr`` element. Child elements of
the ``rPr`` element define the run text style. However, Word adds other ``rPr`` child
elements (see commented-out items in ``_xml_run_formatting_tag_names`` below) that
track spelling and errors, revision history, etc.

Operations on the xml will probably want to ignore "invisible" distinctions between
runs. Runs with matching formatting elements (enumerated in this file) can be joined
without altering the displayed text.

One public function, ``get_visible_run_style`` returns a dictionary describing the
visible run style. The only intended use is as a comparison to other run styles to
determine when visible formatting is identical.

This isn't going to be perfect, because some formatting elements (e.g., ``bCs``)
describe what fonts *would* be used under a given condition, which may or may not
exist. These are more likely copy-and-paste artifacts than intentional formatting
decisions, but docx_reader will see them.

That's a design choice. Comment out bCs, eastAsianLayout, rFonts, cs, and szCs to
ignore these distinctions.

From the WordprocessingML Reference:
https://c-rex.net/projects/samples/ooxml/e1/Part4/OOXML_P4_DOCX_WordprocessingML_topic_ID0EZYAG.html
"""

from enum import Enum
from lxml import etree
from typing import Dict, Set, Tuple
from contextlib import suppress

_xml_run_formatting_tag_names = {
    "b",  # Bold
    "bCs",  # Complex Script Bold
    "bdr",  # Text Border
    "caps",  # Display All Characters As Capital Letters
    "color",  # Run Content Color
    "cs",  # Use Complex Script Formatting on Run
    "dstrike",  # Double Strikethrough
    "eastAsianLayout",  # East Asian Typography Settings
    "effect",  # Animated Text Effect
    "em",  # Emphasis Mark
    "emboss",  # Embossing
    "fitText",  # Manual Run Width
    "highlight",  # Text Highlighting
    "i",  # Italics
    "iCs",  # Complex Script Italics
    "imprint",  # Imprinting
    "kern",  # Font Kerning
    "lang",  # Languages for Run Content
    # "noProof",  # Do Not Check Spelling or Grammar
    "oMath",  # Office Open XML Math
    "outline",  # Display Character Outline
    "position",  # Vertically Raised or Lowered Text
    "rFonts",  # Run Fonts
    # "rPrChange",  # Revision Information for Run Properties
    "rStyle",  # Referenced Character Style
    "rtl",  # Right To Left Text
    "shadow",  # Shadow
    "shd",  # Run Shading
    "smallCaps",  # Small Caps
    "snapToGrid",  # Use Document Grid Settings For Inter-Character Spacing
    "spacing",  # Character Spacing Adjustment
    # "specVanish",  # Paragraph Mark Is Always Hidden
    "strike",  # Single Strikethrough
    "sz",  # Font Size
    "szCs",  # Complex Script Font Size
    "u",  # Underline
    "vanish",  # Hidden Text
    "vertAlign",  # Subscript/Superscript Text
    "w",  # Expanded/Compressed Text
}


_xml_run_formatting_tags = Enum(
    "xml_run_formatting_tags",
    [
        f"{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{x}"
        for x in _xml_run_formatting_tag_names
    ],
)


def get_visible_run_style(
    elem: etree.Element,
) -> Dict[str, Dict[str, str]]:
    """
    Return a dictionary item for each elem in a subset of rPr child elements.

    Filters rPr elements for those that effect the text style. docx_reader will merge
    consecutive run and text elements when ``get_visible_run_style(x)`` is the same
    for each.
    """
    formatting = elem.find(elem.tag + "Pr") or ()
    styles = {}
    for elem in formatting:
        with suppress(KeyError):
            styles[_xml_run_formatting_tags[elem.tag].name] = elem.attrib
    return styles
