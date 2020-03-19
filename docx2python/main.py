#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code (and some other)

:author: Shay Hill
:created: 7/2/2019

Some private methods are here because I wanted to keep them with their tests.
"""
import zipfile
from pathlib import Path
from typing import Optional

from docx2python.docx_context import get_context, pull_image_files
from docx2python.docx_output import DocxContent
from docx2python.docx_text import get_text


def docx2python(
    docx_filename: str,
    image_folder: Optional[str] = None,
    html: bool = False,
    extract_image: bool = True,
) -> DocxContent:
    """Unzip a docx file and extract contents.

    :param docx_filename: path to a docx file
    :param image_folder: optionally specify an image folder
        (images in docx will be copied to this folder)
    :param html: bool, extract some formatting as html
    :param extract_image: bool, extract images from document (default True)
    :return: DocxContent object
    """
    zipf = zipfile.ZipFile(docx_filename)
    context = get_context(zipf)
    context["do_html"] = html

    def file_text(filename_):
        """
        There's a bit of ugly try/except toward the bottom.

        One file in 5300 had the headers and footers mislabeled in
        ``word/_rels.document.xml.rels``. Instead of ``header.xml``, this had the
        header identified as ``word/header.xml``. After trying with
        ``content_dir/file``, try again with just ``file``.
        """
        context["rId2Target"] = {
            x["Id"]: x["Target"] for x in context["content_path2rels"][filename_]
        }

        try:
            unzipped = zipf.read(filename_)
        except KeyError:
            # content dir specified twice
            unzipped = zipf.read("/".join(Path(filename_).parts[1:]))
        return get_text(unzipped, context)

    header = [file_text(filename) for filename in context["headers"]]
    header = [x for y in header for x in y]

    body = file_text(context["officeDocument"])

    footer = [file_text(filename) for filename in context["footers"]]
    footer = [x for y in footer for x in y]

    footnotes = [file_text(filename) for filename in context["footnotes"]]
    footnotes = [x for y in footnotes for x in y]

    endnotes = [file_text(filename) for filename in context["endnotes"]]
    endnotes = [x for y in endnotes for x in y]

    if extract_image:
        images = pull_image_files(zipf, context, image_folder)
    else:
        images = None

    zipf.close()
    return DocxContent(
        header=header,
        body=body,
        footer=footer,
        footnotes=footnotes,
        endnotes=endnotes,
        images=images,
        properties=context["docProp2text"],
    )
