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

from lxml import etree

from .attribute_register import Tags
from .namespace import qn


def _elem_tag_str(elem: etree.Element) -> str:
    """
    The text part of an elem.tag (the portion right of the colon)

    :param elem: an xml element

    create with::

        document = etree.fromstring('bytes string')
        # recursively search document elements.

    **E.g., given**:

        document = etree.fromstring('bytes string')
        # document.tag = '{http://schemas.openxml.../2006/main}:document'
        elem_tag_str(document)

    **E.g., returns**:

        'document'
    """
    return re.match(r"{.*}(?P<tag_name>\w+)", elem.tag).group("tag_name")


# noinspection PyPep8Naming
def _gather_sub_vals(
    element: etree.Element, qname: str = None
) -> Dict[str, Optional[str]]:
    """
    Gather formatting elements for a paragraph or text run.

    :param element: a ``<w:r>`` or ``<w:p>`` xml element. Maybe others
    :param qname: qualified name for child element.

    create with::

        document = etree.fromstring('bytes string')
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


def _gather_Pr(element: etree.Element) -> Dict[str, Optional[str]]:
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
def get_pStyle(paragraph_element: etree.Element) -> str:
    """Collect and format paragraph -> pPr -> pStyle value.

    :param paragraph_element: a ``<w:p>`` xml element

    :return: ``[(pStyle value, '')]``

    Also see docstring for ``gather_pPr``
    """
    return _gather_Pr(paragraph_element).get("pStyle", "")


# noinspection PyPep8Naming
def get_run_formatting(run_element: etree.Element, xml2html) -> List[str]:
    """Select only rPr2 tags you'd like to implement.
    # TODO: redo this docstring

    :param run_element: a ``<w:r>`` xml element

    create with::

        document = etree.fromstring('bytes string')
        # recursively search document for <w:r> elements.

    :return: ``[(rPr, val), (rPr, val) ...]``

    Tuples are always returned in order:

    ``"font"`` first then any other styles in alphabetical order.

    Also see docstring for ``gather_rPr``
    """
    return _format_Pr(_gather_Pr(run_element), xml2html)


# noinspection PyPep8Naming
def get_paragraph_formatting(paragraph_element: etree.Element, xml2html) -> List[str]:
    """Select only rPr2 tags you'd like to implement.
    # TODO: redo this docstring

    :param run_element: a ``<w:r>`` xml element

    create with::

        document = etree.fromstring('bytes string')
        # recursively search document for <w:r> elements.

    :return: ``[(rPr, val), (rPr, val) ...]``

    Tuples are always returned in order:

    ``"font"`` first then any other styles in alphabetical order.

    Also see docstring for ``gather_rPr``
    """
    return _format_Pr({get_pStyle(paragraph_element): None}, xml2html)


def _format_Pr(Pr2val: Dict[str, Union[str, None]], xml2html) -> List[str]:
    """
    Format tags and values into html strings.

    :param Pr2val: tags mapped to values (extracted from xml)
    :return:the interior part of html opening tags, e.g., ['b', 'i', 'font style=""']
    """
    style = []
    groups = defaultdict(list)

    # from formatter, 'font', 'style' ->
    #     ('font', 'style') : [formatter(v[0]), formatter(v[1]), ...]
    for tag, val in ((k, v) for k, v in Pr2val.items() if k in xml2html):
        groups[xml2html[tag][1:]].append(xml2html[tag][0](tag, val))

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


def get_html_formatting(elem: etree.Element, xml2html) -> List[str]:
    """
    Get style for an element (if available)

    :param elem: any element, but it's likely only runs and paragraphs will have a
        useable style.

    :return: ``[(rPr, val), (rPr, val) ...]``
    """
    if elem.tag == Tags.RUN:
        return get_run_formatting(elem, xml2html)
    if elem.tag == Tags.PARAGRAPH:
        return get_paragraph_formatting(elem, xml2html)
    return []


def html_open(style: Sequence[Tuple[str, str]]) -> str:
    """
    HTML tags to open a style.

    >>> style = [
    ...     ("font", 'color="red" size="32"'),
    ...     ("b", ""),
    ...     ("i", ""),
    ...     ("u", ""),
    ... ]
    >>> html_open(style)
    '<font color="red" size="32"><b><i><u>'
    """
    # TODO: update docstrings for style_open and style_close
    return "".join((f"<{x}>" for x in style))


def html_close(style: List[Tuple[str, str]]) -> str:
    """
    HTML tags to close a style.

    >>> style = [
    ...     ("font", 'color="red" size="32"'),
    ...     ("b", ""),
    ...     ("i", ""),
    ...     ("u", ""),
    ... ]
    >>> html_close(style)
    '</u></i></b></font>'

    Tags will always be in reverse (of open) order, so open - close will look like::

        <b><i><u>text</u></i></b>
    """
    return "".join("</{}>".format(x.split()[0]) for x in reversed(style))
