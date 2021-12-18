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

from .attribute_register import Tags, HtmlFormatter
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
    tag_str = re.match(r"{.*}(?P<tag_name>\w+)", elem.tag)
    if tag_str:
        return tag_str.group("tag_name")
    raise RuntimeError("could not get tag from elem")


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

    To keep things more homogeneous, I've given tags like ``<w:b/>`` (bold) a value of
    None, even though they don't take a value in xml.

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
            <w:t>text styled  with rPaa
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
    return _gather_sub_vals(element, element.tag + "Pr")


# noinspection PyPep8Naming
def get_pStyle(paragraph_element: etree.Element) -> str:
    """
    Collect and format paragraph -> pPr -> pStyle value.

    :param paragraph_element: a ``<w:p>`` xml element

    :return: ``[(pStyle value, '')]``

    Also see docstring for ``gather_pPr``
    """
    return _gather_Pr(paragraph_element).get("pStyle", "") or ""


# noinspection PyPep8Naming
def get_run_formatting(
    run_element: etree.Element, xml2html: Dict[str, HtmlFormatter]
) -> List[str]:
    """
    Get run-element formatting converted into html.

    :param run_element: a ``<w:r>`` xml element
        create with::

            document = etree.fromstring('bytes string')
            # recursively search document for <w:r> elements.

    :param xml2html: mapping to convert xml styles to html styles
        e.g., {
            'b': (<function <lambda> at 0x0000026BC7875A60>,),
            'smallCaps': (<function <lambda> at 0x0000026BC7896DC0>, 'font', 'style')
        }

    :return: ``['b', 'i', ...]``

    Lists are always returned in order:

    ``"span"`` first then any other styles in alphabetical order.

    Also see docstring for ``gather_rPr``
    """
    return _format_Pr_into_html(_gather_Pr(run_element), xml2html)


# noinspection PyPep8Naming
def get_paragraph_formatting(
    paragraph_element: etree.Element, xml2html: Dict[str, HtmlFormatter]
) -> List[str]:
    """
    Get paragraph-element formatting converted into html.

    :param paragraph_element: a ``<w:p>`` xml element
        create with::

            document = etree.fromstring('bytes string')
            # recursively search document for <w:r> elements.

    :param xml2html: mapping to convert xml styles to html styles
        e.g., {
            'b': (<function <lambda> at 0x0000026BC7875A60>,),
            'smallCaps': (<function <lambda> at 0x0000026BC7896DC0>, 'font', 'style')
        }

    :return: ``['b', 'i', ...]``

    Tuples are always returned in order:

    ``"font"`` first then any other styles in alphabetical order.

    Also see docstring for ``gather_rPr``
    """
    return _format_Pr_into_html({get_pStyle(paragraph_element): None}, xml2html)


# noinspection PyPep8Naming
def _format_Pr_into_html(
    Pr2val: Dict[str, Union[str, None]], xml2html: Dict[str, HtmlFormatter]
) -> List[str]:
    """
    Format tags and values into html strings.

    :param Pr2val: tags mapped to values (extracted from xml)
        e.g., {'b': None, 'bCs': None}
    :param xml2html: mapping to convert xml styles to html styles
        e.g., {
            'b': (<function <lambda> at 0x0000026BC7875A60>,),
            'smallCaps': (<function <lambda> at 0x0000026BC7896DC0>, 'span', 'style')
        }
    :return: the interior part of html opening tags, eg, ['span style="..."', 'b', 'i']

    Types of styles supported:
    (None, None, formatter -> tag, None)
        -> outside any containers, no value set, e.g., `<b>`
    ('span', 'style', formatter -> tag, val)
        -> inside a span, inside a style property, e.g., `<span style="tag: val">`

    Other formats would probably work, but they aren't necessary to support the tags
    supported (see README).
    """
    style = []

    # group together supported formats with the same container and property_
    # e.g., group together everything that goes into `<span style="$HERE$">`
    # con_pro2for[(con, pro)] = string created from for
    cp2f_keytype = Tuple[Union[None, str], Union[None, str]]
    con_pro2for: defaultdict[cp2f_keytype, List[str]] = defaultdict(list)
    for tag, val in ((k, v) for k, v in Pr2val.items() if k in xml2html):
        formatter, container, property_ = xml2html[tag]
        con_pro2for[(container, property_)].append(formatter(tag, val or ""))

    # group together supported formats with the same container
    # e.g., group together everything that goes into `<span $HERE$>`
    # con2pro_for[(con,)] = string created from pro and for
    con2pro_for: defaultdict[str, List[str]] = defaultdict(list)
    for k, v in sorted((k, v) for k, v in con_pro2for.items() if k[1] is not None):
        con2pro_for[k[0] or ""].append(f'{k[1]}="{";".join(sorted(v))}"')

    # incorporate container type into string
    # style.append(string created from con, pro, and for)
    for k_, v_ in sorted((k, v) for k, v in con2pro_for.items() if k):
        style.append(f"{k_} {' '.join(v_)}")

    # add back in formats with no container or property_
    style += sorted(con_pro2for[(None, None)])
    return style


def get_html_formatting(
    elem: etree.Element, xml2html: Dict[str, HtmlFormatter]
) -> List[str]:
    """
    Get style for an element (if available)

    :param elem: a run or paragraph element.
    :param xml2html: mapping to convert xml styles to html styles
        e.g., {
            'b': (<function <lambda> at 0x0000026BC7875A60>,),
            'smallCaps': (<function <lambda> at 0x0000026BC7896DC0>, 'font', 'style')
        }
    :return: ``[(rPr, val), (rPr, val) ...]``
    """
    if elem.tag == Tags.RUN:
        return get_run_formatting(elem, xml2html)
    if elem.tag == Tags.PARAGRAPH:
        return get_paragraph_formatting(elem, xml2html)
    return []


def html_open(style: Sequence[str]) -> str:
    """
    HTML tags to open a style.

    :param style: sequence of html tags without the '<' and '>'
    :return: opening html tags joined into a single string

    >>> style = ['font color="red" size="32"', 'b', 'i', 'u']
    >>> html_open(style)
    '<font color="red" size="32"><b><i><u>'
    """
    return "".join((f"<{x}>" for x in style))


def html_close(style: List[str]) -> str:
    """
    HTML tags to close a style.

    :param style: sequence of html tags without the '<' and '>'
    :return: closing html tags joined into a single string

    >>> style = ['font color="red" size="32"', 'b', 'i', 'u']
    >>> html_close(style)
    '</u></i></b></font>'

    Tags will always be in reverse (of open) order, so open - close will look like::

        <b><i><u>text</u></i></b>
    """
    return "".join("</{}>".format(x.split()[0]) for x in reversed(style))
