#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Get text run formatting.

:author: Shay Hill
:created: 7/4/2019

Text runs are formatted inline in the ``trash/document.xml`` or header files. Read
those elements to extract formatting information.
"""
import re
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple, Union
from xml.etree import ElementTree

from .attribute_register import Tags
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
def get_pStyle(paragraph_element: ElementTree.Element) -> str:
    """Collect and format paragraph -> pPr -> pStyle value.

    :param paragraph_element: a ``<w:p>`` xml element

    :return: ``[(pStyle value, '')]``

    Also see docstring for ``gather_pPr``
    """
    pStyle = gather_Pr(paragraph_element).get("pStyle")
    if pStyle:
        return pStyle
    return ""


# noinspection PyPep8Naming
def get_run_style(run_element: ElementTree.Element) -> List[str]:
    """Select only rPr2 tags you'd like to implement.
    # TODO: redo this docstring

    :param run_element: a ``<w:r>`` xml element

    create with::

        document = ElementTree.fromstring('bytes string')
        # recursively search document for <w:r> elements.

    :return: ``[(rPr, val), (rPr, val) ...]``

    Tuples are always returned in order:

    ``"font"`` first then any other styles in alphabetical order.

    Also see docstring for ``gather_rPr``
    """
    properties_tag = qn(f'w:{_elem_tag_str(run_element) + "Pr"}')
    return get_Pr_as_html_strings(run_element.find(properties_tag))


# TODO: put run styles into a dictionary with paragraphs styles (mapped to tags)
RUN_STYLES = {
    "b": (lambda tag, val: tag,),
    "i": (lambda tag, val: tag,),
    "u": (lambda tag, val: tag,),
    "strike": (lambda tag, val: "s",),
    # 'dstrike': (lambda tag, val: "del",),
    "vertAlign": (lambda tag, val: val[:3],),  # subscript and superscript
    "smallCaps": (lambda tag, val: "font-variant:small-caps", "font", "style"),
    "caps": (lambda tag, val: "text-transform:uppercase", "font", "style"),
    "highlight": (lambda tag, val: f"background-color:{val}", "span", "style"),
    "sz": (lambda tag, val: f"font-size:{val}pt", "font", "style"),
    "color": (lambda tag, val: f"color:{val}", "font", "style"),
    "Heading1": (lambda tag, val: "h1",),
    "Heading2": (lambda tag, val: "h2",),
    "Heading3": (lambda tag, val: "h3",),
    "Heading4": (lambda tag, val: "h4",),
    "Heading5": (lambda tag, val: "h5",),
    "Heading6": (lambda tag, val: "h6",),
}

# noinspection PyPep8Naming
def get_Pr_as_html_strings(
    properties_elem: Union[ElementTree.Element, None]
) -> List[str]:
    """
    Encode a properties element into a list of html strings.

    :param properties_elem: a ``<w:rPr>`` or ``<w:pPr>`` element. Maybe others.

    create with::

        document = ElementTree.fromstring('bytes string')
        # recursively search document for <w:rPr> or <w:pPr> elements.

    :return: ``['font style="font-size:36"', 'b', 'i' ...]``

    ``"font"`` first then any other styles in alphabetical order.
    """
    if properties_elem is None:
        return []

    Pr2val = {_elem_tag_str(x): x.attrib.get(qn("w:val")) for x in properties_elem}

    style = format_Pr(Pr2val)
    return style


def format_Pr(Pr2val: Dict[str, Union[str, None]]) -> List[str]:
    """
    Format tags and values into html strings.

    :param Pr2val: tags mapped to values (extracted from xml)
    :return:the interior part of html opening tags, e.g., ['b', 'i', 'font style=""']
    """
    style = []
    groups = defaultdict(list)
    # from formatter, 'font', 'style' ->
    #     ('font', 'style') : [formatter(v[0]), formatter(v[1]), ...]
    for tag, val in ((k, v) for k, v in Pr2val.items() if k in RUN_STYLES):
        groups[RUN_STYLES[tag][1:]].append(RUN_STYLES[tag][0](tag, val))
    # from ('font', 'style') : [x, y, z, ...] ->
    #     ('font',) : style={"x; y; z; ..."}
    for k, v in sorted((k, v) for k, v in groups.items() if len(k) == 2):
        groups[(k[0],)].append(f'{k[1]}="{";".join(sorted(v))}"')
    # from ('font',) : string ->
    #     'font string'
    for k, v in sorted((k, v) for k, v in groups.items() if len(k) == 1):
        style.append(f"{k[0]} {' '.join(v)}")
    style += sorted(groups[()])
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
        return get_pStyle(elem)
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
    # TODO: update docstrings for style_open and style_close
    return "".join((f"<{x}>" for x in style))


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
    return "".join("</{}>".format(x.split()[0]) for x in reversed(style))
