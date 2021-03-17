#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code (and some other)

:author: Shay Hill
:created: 7/2/2019

Some private methods are here because I wanted to keep them with their tests.
"""
import zipfile
from typing import Optional

from .attribute_dicts import filter_files_by_type, get_path
from .docx_context import get_context, pull_image_files
from .docx_output import DocxContent
from .docx_text import get_text


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
        Pull the text from a word/something.xml file
        """
        rels = filename_.get("rels", [])
        # TODO: pass rels file objects into context, not Id: Target
        context["rId2Target"] = {x["Id"]: x["Target"] for x in rels}
        unzipped = zipf.read(get_path(filename_))
        return get_text(unzipped, context)

    type2content = {}
    for type_ in ("header", "officeDocument", "footer", "footnotes", "endnotes"):
        type_files = filter_files_by_type(context["files"], type_)
        type_content = sum([file_text(x) for x in type_files], start=[])
        type2content[type_] = type_content

    if extract_image:
        images = pull_image_files(zipf, context, image_folder)
    else:
        images = None

    zipf.close()
    return DocxContent(
        header=type2content["header"],
        body=type2content["officeDocument"],
        footer=type2content["footer"],
        footnotes=type2content["footnotes"],
        endnotes=type2content["endnotes"],
        images=images,
        files=context["files"],
        zipf=zipf,
    )
