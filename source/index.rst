.. docx2python documentation master file, created by
   sphinx-quickstart on Mon Jul  1 08:29:27 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


docx2python
===========

Extract docx headers, footers, text, footnotes, endnotes, properties, and images to a Python object.

The code is an expansion/contraction of [python-docx2txt](https://github.com/ankushshah89/python-docx2txt) (Copyright (c) 2015 Ankush Shah). The original code is mostly gone, but some of the bones may still be here.

**shared features**:

* extracts text from docx files
* extracts images from docx files
* no dependencies (docx2python requires pytest to test)

**additions**:

* extracts footnotes and endnotes
* converts bullets and numbered lists to ascii with indentation
* retains some structure of the original file (more below)
* extracts document properties (creator, lastModifiedBy, etc.)
* inserts image placeholders in text (``'----image1.jpg----'``)
* inserts plain text footnote and endnote references in text (``'----footnote1----'``)
* (optionally) retains font size, font color, bold, italics, and underscore as html
* full test coverage and documentation for developers

**subtractions**:

* no command-line interface
* will only work with later versions of Python


Installation
============

::

    pip install docx2python

Use
===

::

    from docx2python import docx2python

    # extract docx content
    docx2python('path/to/file.docx')

    # extract docx content, write images to image_directory
    docx2python('path/to/file.docx', 'path/to/image_directory')

    # extract docx content with basic font styles converted to html
    docx2python('path/to/file.docx', html=True)

Note on html feature:

* font size, font color, bold, italics, and underline supported
* every tag open in a paragraph will be closed in that paragraph (and, where appropriate, reopened in the next paragraph). If two subsequenct paragraphs are bold, they will be returned as ``<b>paragraph q</b>``, ``<b>paragraph 2</b>``. This is intentional to make  each paragraph its own entity.
* if you specify ``export_font_style=True``, ``>`` and ``<`` in your docx text will be encoded as ``&gt;`` and ``&lt;``

Return Value
============

Function ``docx2python`` returns an object with several attributes.

**header** - contents of the docx headers in the return format described herein

**footer** - contents of the docx footers in the return format described herein

**body** - contents of the docx in the return format described herein

**footnotes** - contents of the docx in the return format described herein

**endnotes** - contents of the docx in the return format described herein

**document** - header  + body + footer + footnotes + endnotes (read only)

**text** - all docx text as one string, similar to what you'd get from `python-docx2txt`

**properties** - docx property names mapped to values (e.g., `{"lastModifiedBy": "Shay Hill"}`)

**images** - image names mapped to images in binary format. Write to filesystem with::

    for name, image in result.images.items():
        with open(name, 'wb') as image_destination:
            write(image_destination, image)

Return Format
=============

Some structure will be maintained. Text will be returned in a nested list, with paragraphs always at depth 4 (i.e., `output.body[i][j][k][l]` will be a paragraph).

If your docx has no tables, output.body will appear as one a table with all contents in one cell::

    [  # document
        [  # table
            [  # row
                [  # cell
                    "Paragraph 1",
                    "Paragraph 2",
                    "-- bulleted list",
                    "-- continuing bulleted list",
                    "1)  numbered list",
                    "2)  continuing numbered list"
                    "    a)  sublist",
                    "        i)  sublist of sublist",
                    "3)  keeps track of indention levels",
                    "    a)  resets sublist counters"
                ]
            ]
         ]
     ]

Table cells will appear as table cells. Text outside tables will appear as table cells.


To preserve the even depth (text always at depth 4), nested tables will appear as new, top-level tables. This is clearer with an example::

    #  docx structure

    [  # document
        [  # table A
            [  # table A row
                [  # table A cell 1
                    "paragraph in table A cell 1"
                ],
                [  # nested table B
                    [  # table B row
                        [  # table B cell
                            "paragraph in table B"
                        ]
                    ]
                ],
                [  # table A cell 2
                    'paragraph in table A cell 2'
                ]
            ]
        ]
    ]

becomes::

    [  # document
        [  # table A
            [  # row in table A
                [  # cell in table A
                    "table A cell 1"
                ]
            ]
        ],
        [  # table B
            [  # row in table B
                [  # cell in table B
                    "table B cell"
                ]
            ]
        ],
        [  # table C
            [  # row in table C
                [  # cell in table C
                    "table A cell 2"
                ]
            ]
        ]
    ]

This ensures text appears

    1) only once
    2) in the order it appears on the docx
    3) always at depth four (i.e., ``result.body[i][j][k][l]`` will be a string).



Helper Functions
================

To assist with future development, every significant function is documented here. The ``iterators`` module is for users. Import these helper functions with::

   from docx2python.iterators import ...

Helpers and recipes documented in the ``docx2python.index`` module.:

* :ref:`modindex`

For developers, all major functions within docx2python. Also serves as a primer on the major files in an extracted ``docx`` file.

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
