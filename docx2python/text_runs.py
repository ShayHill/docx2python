#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Get text run formatting.

:author: Shay Hill
:created: 7/4/2019

Text runs are formatted inline in the ``trash/document.xml`` or header files. Read
those elements to extract formatting information.
"""
import re
from typing import Dict, List, Optional, Sequence, Tuple
from xml.etree import ElementTree
from .attribute_register import Tags
from .attribute_register import has_content

from .namespace import qn


def _elem_tag_str(elem: ElementTree.Element) -> str:
    """
    The text part of an elem.tag (the portion right of the colon)

    :param elem: an xml element

    create with::

        document = ElementTree.fromstring('bytes string')
        # recursively search document elements.

    **E.g., given**:

        document = ElementTree.fromstring('bytes string')
        # document.tag = '{http://schemas.openxml.../2006/main}:document'
        elem_tag_str(document)

    **E.g., returns**:

        'document'
    """
    return re.match(r"{.*}(?P<tag_name>\w+)", elem.tag).group("tag_name")


# noinspection PyPep8Naming
def _gather_sub_vals(
    element: ElementTree.Element, qname: str = None
) -> Dict[str, Optional[str]]:
    """
    Gather formatting elements for a paragraph or text run.

    :param element: a ``<w:r>`` or ``<w:p>`` xml element. Maybe others
    :param qname: qualified name for child element.

    create with::

        document = ElementTree.fromstring('bytes string')
        # recursively search document for <w:r> elements.

    :return: Style names ('b/', 'sz', etc.) mapped to values.

    To keep things more homogeneous, I've given tags list b/ (bold) a value of None,
    even though they don't take a value in xml.

    Each element of rPr will be either present (returned tag: None) or have a value
    (returned tag: val).

    **E.g., given**::

         <w:r w:rsidRPr="000E1B98">
            <w:rPr>
                <w:rFonts w:ascii="Arial"/>
                <w:b/>
                <w:sz w:val="32"/>
                <w:szCs w:val="32"/>
                <w:u w:val="single"/>
            </w:rPr>
            <w:t>text styled  with rPr
            </w:t>
        </w:r>

    **E.g., returns**::

        {
            "rFonts": True,
            "b": None,
            "u": "single",
            "i": None,
            "sz": "32",
            "color": "red",
            "szCs": "32",
        }
    """
    try:
        sub_element = element.find(qname)
        return {_elem_tag_str(x): x.attrib.get(qn("w:val"), None) for x in sub_element}
    except TypeError:
        # no formatting for element
        return {}


def gather_Pr(element: ElementTree.Element) -> Dict[str, Optional[str]]:
    """
    Gather style values for a <w:r> or <w:p> element (maybe others)

    :param element: any xml element. r and p elems typically have Pr values.
    :return: Style names ('b/', 'sz', etc.) mapped to values.

    Will infer a style element qualified name: p -> pPr; r -> rPr

    Call this with any element. Runs and Paragraphs may have a Pr element. Most
    elements will not, but the function will will quietly return an empty dict.
    """
    qname = qn(f"w:{element.tag.split('}')[-1]}Pr")
    return _gather_sub_vals(element, qname)


# noinspection PyPep8Naming
def get_paragraph_style(
    paragraph_element: ElementTree.Element,
) -> List[Tuple[str, str]]:
    """Collect and format paragraph -> pPr -> pStyle value.

    :param paragraph_element: a ``<w:p>`` xml element

    :return: ``[(pStyle value, '')]``

    Also see docstring for ``gather_pPr``
    """
    pStyle = gather_Pr(paragraph_element).get("pStyle")
    if pStyle:
        return [(pStyle, "")]
    return []


# noinspection PyPep8Naming
def get_run_style(run_element: ElementTree.Element) -> List[Tuple[str, str]]:
    """Select only rPr2 tags you'd like to implement.

    :param run_element: a ``<w:r>`` xml element

    create with::

        document = ElementTree.fromstring('bytes string')
        # recursively search document for <w:r> elements.

    :return: ``[(rPr, val), (rPr, val) ...]``

    Tuples are always returned in order:

    ``"font"`` first then any other styles in alphabetical order.

    Also see docstring for ``gather_rPr``
    """
    rPr2val = gather_Pr(run_element)
    style = []
    font_styles = []

    for tag, val in sorted(rPr2val.items()):
        if tag in {"b", "i", "u"}:
            style.append((tag, ""))
        elif tag == "sz":
            font_styles.append('size="{}"'.format(val))
        elif tag == "color":
            font_styles.append('color="{}"'.format(val))

    if font_styles:
        style = [("font", " ".join(sorted(font_styles)))] + style
    return style


def get_style(elem: ElementTree.Element) -> List[Tuple[str, str]]:
    """
    Get style for an element (if available)

    :param elem: any element, but it's likely only runs and paragraphs will have a
        useable style.

    :return: ``[(rPr, val), (rPr, val) ...]``
    """
    if elem.tag == Tags.RUN:
        return get_run_style(elem)
    if elem.tag == Tags.PARAGRAPH:
        return get_paragraph_style(elem)
    return []


def style_open(style: Sequence[Tuple[str, str]]) -> str:
    """
    HTML tags to open a style.

    >>> style = [
    ...     ("font", 'color="red" size="32"'),
    ...     ("b", ""),
    ...     ("i", ""),
    ...     ("u", ""),
    ... ]
    >>> style_open(style)
    '<font color="red" size="32"><b><i><u>'
    """
    text = [" ".join(x for x in y if x) for y in style]
    return "".join("<{}>".format(x) for x in text)


def style_close(style: List[Tuple[str, str]]) -> str:
    """
    HTML tags to close a style.

    >>> style = [
    ...     ("font", 'color="red" size="32"'),
    ...     ("b", ""),
    ...     ("i", ""),
    ...     ("u", ""),
    ... ]
    >>> style_close(style)
    '</u></i></b></font>'

    Tags will always be in reverse (of open) order, so open - close will look like::

        <b><i><u>text</u></i></b>
    """
    return "".join("</{}>".format(x) for x, _ in reversed(style))
