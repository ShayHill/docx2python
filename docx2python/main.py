#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code (and some other)

:author: Shay Hill
:created: 7/2/2019

Some private methods are here because I wanted to keep them with their tests.
"""
import zipfile
from typing import Optional

from .globs import DocxContext, File
from .attribute_dicts import filter_files_by_type, get_path
from .docx_context import get_context, pull_image_files
from .docx_output import DocxContent
from .docx_text import get_text


def docx2python(
    docx_filename: str,
    image_folder: Optional[str] = None,
    html: bool = False,
    paragraph_styles: bool = False,
    extract_image: bool = True,
) -> DocxContent:
    """Unzip a docx file and extract contents.

    :param docx_filename: path to a docx file
    :param image_folder: optionally specify an image folder
        (images in docx will be copied to this folder)
    :param html: bool, extract some formatting as html
    :param paragraph_styles: prepend the paragraphs style (if any, else "") to each
        paragraph. This will only be useful with ``*_runs`` attributes.
    :param extract_image: bool, extract images from document (default True)
    :return: DocxContent object
    """
    zipf = zipfile.ZipFile(docx_filename)
    docx_context = DocxContext(
        docx_filename, image_folder, html, paragraph_styles, extract_image
    )

    def file_text(filename_):
        """
        Pull the text from a word/something.xml file
        """
        return get_text(file=filename_)

    type2content = {}
    for type_ in ("header", "officeDocument", "footer", "footnotes", "endnotes"):
        type_files = docx_context.files_of_type(type_)
        type_content = sum([file_text(x) for x in type_files], start=[])
        type2content[type_] = type_content

    # TODO: factor this out to return value
    if extract_image:
        images = pull_image_files(docx_context, image_folder)
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
        files=docx_context.files,
        zipf=zipf,
        context=docx_context,
    )


# TODO: sort headers and footers
# TODO: remove this block
if __name__ == "__main__":
    # TODO: run the CRB manual again and have a look at the hyperlinks
    from time import time

    TIME = time.time()
    pars = docx2python("test/resources/CRB EHS Manual.docx", html=True)
    total_time = time.time() - TIME
    print(f"{total_time=}")
    breakpoint()
