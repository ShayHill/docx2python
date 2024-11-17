"""Register namespace entries in xml ``document`` elements.

:author: Shay Hill
:created: 7/5/2019

A ``<w:document>`` element at the top of each xml file defines a namespace::

    <w:document
        xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    />

These entries can be accessed in the file by their abbreviations::

    <w:p>
        contents of paragraph
    </w:p>

``lxml.etree`` reads ``"<w:p>"`` as

``"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"``

This module defines the necessary namespaces and transforms ``"w:p"`` to
``{http://...}p``. This allows readable code like::

    if element.tag == qn("w:p"):

instead of::

    if element.tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p":

If somewhere along the line this package just stops working, it may be that the NSMAP
entries have been updated for whatever docx you're working with (though that's not
supposed to ever happen). *If* this happens::

    1) Unzip the docx.
    2) open ``word/document.xml`` in a text editor.
    3) Search for xmlns:w=[some string]
    4) update NSMAP['w'] = some string

Lxml allows (deceptively) easy access to a file's namespaces; however, this is
problematic because ``root_element.nsmap`` may not retrieve all nsmap entries. Other
entries may be buried inside sub-environments further down in the tree. It is safer
to explicate namespace mapping.

If you extend docx2text with other tags, additional NSMAP entries may be necessary.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from docx2python.attribute_register import get_prefixed_tag

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore


def qn(elem: EtreeElement, tag: str) -> str:
    """Turn a namespace-prefixed tag into a Clark-notation qualified tag.

    :param elem: lxml.etree._Element object
    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: Clark-notation qualified tag,
        e.g. ``{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p``
        IN THE NAMESPACES DEFINED IN THE ``elem`` ELEMENT

    Most lxml elements contain the entire namespace of their parent elements. Create
    a tag within this namespace.

    Stands for 'qualified name', a utility function to turn a namespace prefixed tag
    name into a Clark-notation qualified tag name for lxml.

        >>> qn('w:cSld')
        '{http://schemas.../main}cSld'

    Source: https://github.com/python-openxml/python-docx/
    """
    prefix, localname = tag.split(":")
    uri = elem.nsmap[prefix]
    return f"{{{uri}}}{localname}"


def get_attrib_by_qn(elem: EtreeElement, tag: str) -> str:
    """Get the attribute of an element by a namespace-prefixed tag.

    :param elem: lxml.etree._Element object
    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: attribute of the element with the namespace-prefixed tag
    """
    return elem.attrib[qn(elem, tag)]


def find_by_qn(elem: EtreeElement, tag: str) -> EtreeElement | None:
    """Find next element in the tree with a namespace-prefixed tag.

    :param elem: lxml.etree._Element object
    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: next element with the namespace-prefixed tag
    """
    return elem.find(qn(elem, tag))


def findall_by_qn(elem: EtreeElement, tag: str) -> list[EtreeElement]:
    """Find all elements in the tree with a namespace-prefixed tag.

    :param elem: lxml.etree._Element object
    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: list of elements with the namespace-prefixed tag
    """
    return elem.findall(qn(elem, tag))


def find_parent_by_qn(elem: EtreeElement | None, tag: str) -> EtreeElement | None:
    """Find the parent element in the tree with a namespace-prefixed tag.

    :param elem: lxml.etree._Element object
    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: parent element with the namespace-prefixed tag
    """
    if elem is None:
        return None
    if get_prefixed_tag(elem) == tag:
        return elem
    return find_parent_by_qn(elem.getparent(), tag)


def iterfind_by_qn(elem: EtreeElement, tag: str) -> Iterator[EtreeElement]:
    """Iterate over all elements in the tree with a namespace-prefixed tag.

    :param elem: lxml.etree._Element object
    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: iterator over elements with the namespace-prefixed tag
    """
    yield from elem.iterfind(qn(elem, tag))
