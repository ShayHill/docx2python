""" Content from files that aren't ``word/document.xml``

:author: Shay Hill
:created: 6/26/2019

Most of the "meat" in a docx file is in ``word/document.xml``. These functions retrieve
numbering formats, images, and font styles from *other* files in a decompressed docx.
"""
from __future__ import annotations

import re
import zipfile

from lxml import etree
from lxml.etree import _Element as EtreeElement  # type: ignore

from .namespace import qn


def collect_numFmts(numFmts_root: EtreeElement) -> dict[str, list[str]]:
    """
    Collect abstractNum bullet formats into a dictionary

    :param numFmts_root: Root element of ``word/numbering.xml``.
    :return: numId mapped to numFmts (by ilvl)

    :background:

    ``word/numbering.xml`` will have two sections.

    **SECTION 1** - Some abstractNum elements defining numbering formats for multiple
    indentation levels::

        <w:abstractNum w:abstractNumId="0">
            <w:lvl w:ilvl="0"><w:numFmt w:val="decimal"/></w:lvl>
            <w:lvl w:ilvl="1"><w:numFmt w:val="lowerLetter"/></w:lvl>
            ...
        </w:abstractNum>

    **SECTION 2** - Some num elements, each referencing an abstractNum. Multiple nums
    may reference the same abstractNum, but each will maintain a separate count (i.e.,
    each numbered paragraph will start from 1, even if it shares a style with another
    paragraph.)::

        <w:num w:numId="1">
            <w:abstractNumId w:val="0"/>
        </w:num>
        <w:num w:numId="2">
            <w:abstractNumId w:val="5"/>
        </w:num>

    **E.g, Given**: *above*

    **E.g., Returns**::

        {
            # -----ilvl=0------ilvl=1------ilvl=2---
            "1": ["decimal", "lowerLetter", ...],
            "2": ...
        }
    """
    abstractNumId2numFmts: dict[str, list[str]] = {}

    for abstractNum in numFmts_root.findall(qn("w:abstractNum")):
        id_ = str(abstractNum.attrib[qn("w:abstractNumId")])
        abstractNumId2numFmts[id_] = []
        for lvl in abstractNum.findall(qn("w:lvl")):
            numFmt = lvl.find(qn("w:numFmt"))
            if numFmt is not None:
                abstractNumId2numFmts[id_].append(str(numFmt.attrib[qn("w:val")]))

    numId2numFmts: dict[str, list[str]] = {}
    num: EtreeElement
    for num in (x for x in numFmts_root.findall(qn("w:num"))):
        numId = num.attrib[qn("w:numId")]
        abstractNumId = num.find(qn("w:abstractNumId"))
        if abstractNumId is None:
            continue
        abstractNumIdval = abstractNumId.attrib.get(qn("w:val"))
        numId2numFmts[str(numId)] = abstractNumId2numFmts[str(abstractNumIdval)]

    return numId2numFmts


def collect_rels(zipf: zipfile.ZipFile) -> dict[str, list[dict[str, str]]]:
    """
    Map file to relId to attrib

    :param zipf: created by ``zipfile.ZipFile("docx_filename")``
    :return: a deep dictionary ``{filename: list of Relationships``

    Each rel in list of Relationships is::

        {
            "Id": "rId1",
            "Type": "http...",
            "Target": "path to file in docx"
        }

    There are several rels files:

    ``_rels/.rels``: rels related to entire structure.  The identity of
        ``word/document.xml`` is here. (It might be called ``word/document2.xml`` or
        something else. Checking here is the best way to make sure.)

    ``word/_rels/document.xml.rels``: images, headers, etc. referenced by
        ``word/document.xml``

    ``word/_rels/header1.xml.rels``: images, etc. for ``header1.xml``

    ...

    Get everything from everywhere. Map ``_rels/.rels`` to ``'rels'`` and everything
    else to e.g., ``'document'`` or ``'header'``. RelIds are **not** unique between
    these files.

    **E.g, Given**::

    # one of several files

        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.../relationships">
            <Relationship Id="rId3" Type="http://schemas... \
                /extended-properties" Target="docProps/app.xml"/>
            <Relationship Id="rId2" Type="http://schemas... \
                /core-properties" Target="docProps/core.xml"/>
            <Relationship Id="rId1" Type="http://schemas... \
                /officeDocument" Target="word/document.xml"/>
            <Relationship Id="rId4" Type="http://schemas... \
                /custom-properties" Target="docProps/custom.xml"/>
        </Relationships>

    **Returns**::

        {
            "filename": [
                {
                    "Id": "rId3",
                    "Type": "http://schemas.../extended-properties",
                    "Target": "docProps/app.xml",
                },
                {
                    "Id": "rId2",
                    "Type": "http://schemas.../core-properties",
                    "Target": "docProps/core.xml",
                },
            ]
        }
    """
    path2rels: dict[str, list[dict[str, str]]] = {}
    for rels in (x for x in zipf.namelist() if x[-5:] == ".rels"):
        path2rels[rels] = [
            {str(y): str(z) for y, z in x.attrib.items()}
            for x in etree.fromstring(zipf.read(rels))
        ]
    return path2rels


def collect_docProps(root: EtreeElement) -> dict[str, str | None]:
    """
    Get author, modified, etc. from core-properties (should be docProps/core.xml)

    :param root: root of the XML tree
    :return: document property names mapped to values

    **E.g., Given**::

        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats...">
            <dc:title>SG-DOP-5009 - Operate ROMAR swarf unit
            </dc:title>
            <dc:creator>Shay Hill
            </dc:creator>
            <cp:lastModifiedBy>Shay Hill
            </cp:lastModifiedBy>
            <cp:revision>6
            </cp:revision>
            <cp:lastPrinted>2017-11-17T15:47:00Z
            </cp:lastPrinted>
            <dcterms:created xsi:type="dcterms:W3CDTF">2019-01-10T07:21:00Z
            </dcterms:created>
            <dcterms:modified xsi:type="dcterms:W3CDTF">2019-01-11T11:41:00Z
            </dcterms:modified>
        </cp:coreProperties>

    **E.g., Returns**::

        {
            "title": "SG-DOP-5009 - Operate ROMAR swarf unit",
            "creator": "Shay Hill",
            "lastModifiedBy": "Shay Hill",
            "revision": "6",
            ...
        }
    """
    docProp2text: dict[str, str | None] = {}
    capture_tag_name = re.compile(r"{.+}(?P<tag_name>\w+)")
    for dc in root:
        tag_match = re.match(capture_tag_name, dc.tag)
        if tag_match:
            docProp2text[tag_match.group("tag_name")] = dc.text
    return docProp2text
