#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code (and some other)

:author: Shay Hill
:created: 7/2/2019

Some private methods are here because I wanted to keep them with their tests.
"""
import re
import zipfile
from typing import Optional

from docx2python.docx_context import get_context, pull_image_files
from docx2python.docx_output import DocxContent
from docx2python.docx_text import get_text


def docx2python(
    docx_filename: str, image_folder: Optional[str] = None, html: bool = False
) -> DocxContent:
    """Unzip a docx file and extract contents."""
    zipf = zipfile.ZipFile(docx_filename)
    context = get_context(zipf)
    context["do_html"] = html

    def file_text(filename_):
        context["rId2Target"] = {
            x["Id"]: x["Target"] for x in context["content_path2rels"][filename_]
        }
        return get_text(zipf.read(filename_), context)

    header = [file_text(filename) for filename in context["headers"]]
    header = [x for y in header for x in y]

    body = file_text(context["officeDocument"])

    footer = [file_text(filename) for filename in context["footers"]]
    footer = [x for y in footer for x in y]

    footnotes = [file_text(filename) for filename in context["footnotes"]]
    footnotes = [x for y in footnotes for x in y]

    endnotes = [file_text(filename) for filename in context["endnotes"]]
    endnotes = [x for y in endnotes for x in y]

    images = pull_image_files(zipf, context, image_folder)

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
