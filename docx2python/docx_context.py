#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Content from files that aren't ``word/document.xml``

:author: Shay Hill
:created: 6/26/2019

Most of the "meat" in a docx file is in ``word/document.xml``. These functions retrieve
numbering formats, images, and font styles from *other* files in a decompressed docx.

Several functions here take a bytes-format document from a decompressed docx.file.
Create such with::

            import zipfile

            zipf = zipfile.ZipFile("docx_filename.docx")
            xml = zipf.read("trash/numbering.xml")
"""
import os
import pathlib
import re
import zipfile
from collections import defaultdict
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

# namespace map. see qn
from docx2python.namespace import qn


# noinspection PyPep8Naming
def collect_numFmts(xml: bytes) -> Dict[str, List[str]]:
    """
    Collect abstractNum bullet formats into a dictionary

    :param xml: ``trash/numbering.xml`` from a decompressed docx file

    :returns: numId mapped to numFmts (by ilvl)

    :background:

    ``trash/numbering.xml`` will have two sections.

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
            "1": ["decimal", "lowerLetter", ...],
            "2": ...
        }
    """
    abstractNumId2numFmts = {}

    root = ElementTree.fromstring(xml)
    for abstractNum in root.findall(qn("w:abstractNum")):
        id_ = abstractNum.attrib[qn("w:abstractNumId")]
        abstractNumId2numFmts[id_] = []
        for lvl in abstractNum.findall(qn("w:lvl")):
            numFmt = lvl.find(qn("w:numFmt"))
            abstractNumId2numFmts[id_].append(numFmt.attrib[qn("w:val")])

    numId2numFmts = {}
    for num in root.findall(qn("w:num")):
        numId = num.attrib[qn("w:numId")]
        abstractNumId = num.find(qn("w:abstractNumId")).attrib[qn("w:val")]
        numId2numFmts[numId] = abstractNumId2numFmts[abstractNumId]

    return numId2numFmts


def collect_rels(zipf: zipfile.ZipFile) -> Dict[str, List[Dict[str, str]]]:
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
    ``word/document.xml`` is here. (It might be called
    ``word/document2.xml`` or something else. Checking here is the best way
    to make sure.)

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
    path2rels = {}
    for rels in (x for x in zipf.namelist() if x[-5:] == ".rels"):
        path2rels[rels] = [x.attrib for x in ElementTree.fromstring(zipf.read(rels))]
    return path2rels


# noinspection PyPep8Naming
def collect_docProps(xml: bytes) -> Dict[str, str]:
    # noinspection SpellCheckingInspection
    """ Get author, modified, etc. from docProps

        :param xml: ``DocProps/core.xml`` from a decompressed docx file
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
    docProp2text = {}
    root = ElementTree.fromstring(xml)
    for dc in root:
        docProp2text[re.match(r"{.+}(\w+)", dc.tag).group(1)] = dc.text
    return docProp2text


def get_path_rels(path: str) -> str:
    """
    Get path/to/rels for path/to/xml

    :param path: path to a docx content file.
    :returns: path to rels (which may not exist)

    Every content file (``document.xml``, ``header1.xml``, ...) will have its own
    ``.rels`` file--if any relationships are defined.
    """
    folder, file = os.path.split(path)
    return "".join([folder, "/_rels/", file, ".rels"])


# noinspection PyPep8Naming
def get_context(zipf: zipfile.ZipFile) -> Dict[str, Any]:
    """
    Collect context information from docProps, rels etc.

    :param zipf: created by ``zipfile.ZipFile("docx_filename")``
    :return: dictionaries

        * rId2Target - rel Id mapped to image files
        * docProp2text - document properties like 'modified' and 'created'
        * numId2numFmts - paragraph IDs mapped to number and bullet formats
        * numIdcount - a counter starting at 0 for each ilvl of each numbered list

        The last two will only be present in documents with bulleted or numbered lists.
    """
    path2rels = collect_rels(zipf)
    officeDocument = next(
        x["Target"]
        for x in path2rels["_rels/.rels"]
        if os.path.basename(x["Type"]) == "officeDocument"
    )
    officeDocument_rels = get_path_rels(officeDocument)
    content_dir = os.path.dirname(officeDocument)

    headers, footers, endnotes, footnotes = [], [], [], []
    for rel in path2rels[officeDocument_rels]:
        rel_type = os.path.basename(rel["Type"])
        if rel_type == "header":
            headers.append("/".join([content_dir, rel["Target"]]))
        elif rel_type == "footer":
            footers.append("/".join([content_dir, rel["Target"]]))
        elif rel_type == "footnotes":
            footnotes.append("/".join([content_dir, rel["Target"]]))
        elif rel_type == "endnotes":
            endnotes.append("/".join([content_dir, rel["Target"]]))

    content_path2rels = {
        x: path2rels.get(get_path_rels(x), {})
        for x in [officeDocument] + headers + footers + footnotes + endnotes
    }

    context = {
        "content_dir": content_dir,
        "officeDocument": officeDocument,
        "headers": headers,
        "footers": footers,
        "footnotes": footnotes,
        "endnotes": endnotes,
        "content_path2rels": content_path2rels,
        "docProp2text": collect_docProps(zipf.read("docProps/core.xml")),
    }
    try:
        numId2numFmts = collect_numFmts(zipf.read("word/numbering.xml"))
        context["numId2numFmts"] = numId2numFmts
        context["numId2count"] = {
            x: defaultdict(lambda: 0) for x in numId2numFmts.keys()
        }
    except KeyError:
        # no bullets or numbered paragraphs in file
        pass
    return context


def pull_image_files(
    zipf: zipfile.ZipFile,
    context: Dict[str, Any],
    image_directory: Optional[str] = None,
) -> Dict[str, bytes]:
    """
    Copy images from zip file.

    :param zipf: created by ``zipfile.ZipFile(docx_filename)``
    :param image_directory: optional destination for copied images
    :param context: dictionary of document attributes generated in ``get_context``
    :return: Image names mapped to images in binary format.

        To write these to disc::

            with open(key, 'wb') as file:
                file.write(value)

    :side effects: Given an optional image_directory, will write the images out to file.
    """
    images = {
        os.path.basename(x): zipf.read(x)
        for x in zipf.namelist()
        if re.match(context["content_dir"] + r"/media/image\d+", x)
    }
    if image_directory is not None:
        pathlib.Path(image_directory).mkdir(parents=True, exist_ok=True)
        for file, image in images.items():
            with open(os.path.join(image_directory, file), "wb") as image_copy:
                image_copy.write(image)
    return images
