# docx2python

Extract docx headers, footers, text, footnotes, endnotes, properties, and images to a Python object.

[full documentation](https://docx2python.readthedocs.io/en/latest/index.html)

The code is an expansion/contraction of [python-docx2txt](https://github.com/ankushshah89/python-docx2txt) (Copyright (c) 2015 Ankush Shah). The original code is mostly gone, but some of the bones may still be here.

__shared features__:
* extracts text from docx files
* extracts images from docx files
* no dependencies (docx2python requires pytest to test)

__additions:__
* extracts footnotes and endnotes
* converts bullets and numbered lists to ascii with indentation
* retains some structure of the original file (more below)
* extracts document properties (creator, lastModifiedBy, etc.)
* inserts image placeholders in text (``'----image1.jpg----'``)
* inserts plain text footnote and endnote references in text (``'----footnote1----'``)
* (optionally) retains font size, font color, bold, italics, and underscore as html
* full test coverage and documentation for developers
  
__subtractions:__
* no command-line interface
* will only work with later versions of Python


## Installation
```bash
pip install docx2python
```

## Use

```python
from docx2python import docx2python

# extract docx content
docx2python('path/to/file.docx')

# extract docx content, write images to image_directory
docx2python('path/to/file.docx', 'path/to/image_directory')

# extract docx content with basic font styles converted to html
docx2python('path/to/file.docx', html=True)
```

Note on html feature:
* font size, font color, bold, italics, and underline supported
* every tag open in a paragraph will be closed in that paragraph (and, where appropriate, reopened in the next paragraph). If two subsequenct paragraphs are bold, they will be returned as `<b>paragraph q</b>`, `<b>paragraph 2</b>`. This is intentional to make  each paragraph its own entity. 
* if you specify `export_font_style=True`, `>` and `<` in your docx text will be encoded as `&gt;` and `&lt;`

## Return Value

Function `docx2python` returns an object with several attributes.

__header__ - contents of the docx headers in the return format described herein

__footer__ - contents of the docx footers in the return format described herein

__body__ - contents of the docx in the return format described herein

__footnotes__ - contents of the docx in the return format described herein

__endnotes__ - contents of the docx in the return format described herein

__document__ - header  + body + footer (read only)

__text__ - all docx text as one string, similar to what you'd get from `python-docx2txt`

__properties__ - docx property names mapped to values (e.g., `{"lastModifiedBy": "Shay Hill"}`)

__images__ - image names mapped to images in binary format. Write to filesystem with

```
for name, image in result.images.items():
    with open(name, 'wb') as image_destination:
        write(image_destination, image)
```

## Return Format

Some structure will be maintained. Text will be returned in a nested list, with paragraphs always at depth 4 (i.e., `output.body[i][j][k][l]` will be a paragraph).

If your docx has no tables, output.body will appear as one a table with all contents in one cell:

```python
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
```

Table cells will appear as table cells. Text outside tables will appear as table cells.


To preserve the even depth (text always at depth 4), nested tables will appear as new, top-level tables. This is clearer with an example:

```python
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
```

becomes ...
```python
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
```

This ensures text appears

1. only once
1. in the order it appears on the docx
1. always at depth four (i.e., `result.body[i][j][k][l]` will be a string).
    
## Working with output

This package provides several documented helper functions in [the ``docx2python.iterators`` module](https://docx2python.readthedocs.io/en/latest/docx2python.html#module-iterators). Here are a few recipes possible with these functions:

```python
from docx2python.iterators import enum_cells

def remove_empty_paragraphs(tables):
    for (i, j, k), cell in enum_cells(tables):
        tables[i][j][k] = [x for x in cell if x]
```

```
>>> tables = [[[['a', 'b'], ['a', '', 'd', '']]]]
>>> remove_empty_paragraphs(tables)
    [[[['a', 'b'], ['a', 'd']]]]
```

```python
from docx2python.iterators import enum_at_depth

def html_map(tables) -> str:
    """Create an HTML map of document contents.

    Render this in a browser to visually search for data.
    """
    tables = self.document

    # prepend index tuple to each paragraph
    for (i, j, k, l), paragraph in enum_at_depth(tables, 4):
        tables[i][j][k][l] = " ".join([str((i, j, k, l)), paragraph])

    # wrap each paragraph in <pre> tags
    for (i, j, k), cell in enum_at_depth(tables, 3):
        tables[i][j][k] = "".join([f"<pre>{x}</pre>" for x in cell])

    # wrap each cell in <td> tags
    for (i, j), row in enum_at_depth(tables, 2):
        tables[i][j] = "".join([f"<td>{x}</td>" for x in row])

    # wrap each row in <tr> tags
    for (i,), table in enum_at_depth(tables, 1):
        tables[i] = "".join(f"<tr>{x}</tr>" for x in table)

    # wrap each table in <table> tags
    tables = "".join([f'<table border="1">{x}</table>' for x in tables])

    return ["<html><body>"] + tables + ["</body></html>"]
```

```
>>> tables = [[[['a', 'b'], ['a', 'd']]]]
>>> html_toc(tables)
<html>
    <body>
        <table border="1">
            <tr>
                <td>
                    '(0, 0, 0, 0) a'
                    '(0, 0, 0, 1) b'
                </td>
                <td>
                    '(0, 0, 1, 0) a'
                    '(0, 0, 1, 1) d'
                </td>
            </tr>
        </table>
    </body>
</html>
```

[See helper functions.](https://docx2python.readthedocs.io/en/latest/index.html)
