r"""Break up long lines in an unzipped docx file

:author: Shay Hill
:created: 11/15/2020

A docx file is just a group of xml files zipped up. To examine an xml file in Widows:
    * rename file.docx to file.zip
    * unzip file.zip

This is useful for examining the xml to debug issues or find how the xml works.
However, opening these unzipped xml files in an editor can be problematic because
they're all one line. That chokes the editor.

This script just reads through an unzipped xml file and replaces `><` with `>\n<`.

That's enough formatting to open and read through the file.
"""

import re


def break_long_xml_lines(filename: str) -> None:
    r"""
    Replace `><` with `>\n<`. Overwrite original file.

    :param filename: an xml file (inside an unzipped docx)
    """
    with open(filename, "rb") as one_line:
        lines = one_line.readlines()
    lines = [re.sub(b"><", b">\n<", x) for x in lines]
    with open(filename, "wb") as split_lines:
        _ = split_lines.write(b"\n".join(lines))
