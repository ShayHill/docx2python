#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Register namespace entries in xml ``document`` elements.

:author: Shay Hill
:created: 7/5/2019

A ``<w:document>`` element at the top of each xml file defines a namespace::

    <w:document
        xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    >

These entries can be accessed in the file by their abbreviations::

    <w:p>
        contents of paragraph
    </w:p>

``xml.etree`` in the Python standard docx2python reads ``"<w:p>"`` as

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
"""

NSMAP = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}


def qn(tag: str) -> str:
    """Turn a namespace-prefixed tag into a Clark-notation qualified tag.

    Stands for 'qualified name', a utility function to turn a namespace prefixed tag
    name into a Clark-notation qualified tag name for lxml.

        >>> qn('w:cSld')
        '{http://schemas.../main}cSld'

    Source: https://github.com/python-openxml/python-docx/
    """
    prefix, tagroot = tag.split(":")
    uri = NSMAP[prefix]
    return "{{{}}}{}".format(uri, tagroot)
