# docx2python

Extract docx headers, footers, text, footnotes, endnotes, properties, and images to a Python object.

`README_DOCX_FILE_STRUCTURE.md` may help if you'd like to extend docx2python.

For a summary of what's new in docx2python 2, scroll down to **New in docx2python Version 2**

The code is an expansion/contraction of [python-docx2txt](https://github.com/ankushshah89/python-docx2txt) (Copyright (c) 2015 Ankush Shah). The original code is mostly gone, but some of the bones may still be here.

__shared features__:
* extracts text from docx files
* extracts images from docx files

__additions:__
* extracts footnotes and endnotes
* converts bullets and numbered lists to ascii with indentation
* converts hyperlinks to ``<a href="http:/...">link text</a>``
* retains some structure of the original file (more below)
* extracts document properties (creator, lastModifiedBy, etc.)
* inserts image placeholders in text (``'----image1.jpg----'``)
* inserts plain text footnote and endnote references in text (``'----footnote1----'``)
* (optionally) retains font size, font color, bold, italics, and underscore as html
* extract math equations
* extract user selections from checkboxes and dropdown menus

__subtractions:__
* no command-line interface
* will only work with Python 3.8+


## Installation
```bash
pip install docx2python
```

## Use

``` python
from docx2python import docx2python

# extract docx content
with docx2python('path/to/file.docx') as docx_content:
    print(docx_content.text)

docx_content = docx2python('path/to/file.docx')
print(docx_content.text)
docx_content.close()

# extract docx content, write images to image_directory
with docx2python('path/to/file.docx', 'path/to/image_directory') as docx_content:
    print(docx_content.text)

# extract docx content with basic font styles converted to html
with docx2python('path/to/file.docx', html=True) as docx_content:
    print(docx_content.text)
```

`docx2python` opens a zipfile object and (lazily) reads it. Use context management (`with ... as`) to close this zipfile object or explicitly close with `docx_content.close()`.

Note on html feature:
* supports ``<i>``italic, ``<b>``bold, ``<u>``underline, ``<s>``strike, ``<sup>``superscript, ``<sub>``subscript, ``<span style="font-variant: small-caps">``small caps, ``<span style="text-transform:uppercase">``all caps, ``<span style="background-color: yellow">``highlighted, ``<span style="font-size:32">``font size, ``<span style="color:#ff0000">``colored text.
* hyperlinks will always be exported as html (``<a href="http:/...">link text</a>``), even if ``html=False``, because I couldn't think of a more canonical representation.
* every tag open in a paragraph will be closed in that paragraph (and, where appropriate, reopened in the next paragraph). If two subsequenct paragraphs are bold, they will be returned as `<b>paragraph a</b>`, `<b>paragraph b</b>`. This is intentional to make  each paragraph its own entity.
* if you specify `html=True`, `&`, `>` and `<` in your docx text will be encoded as `&amp`, `&gt;` and `&lt;`

## Return Value

Function `docx2python` returns a DocxContent instance with several attributes.

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

# or

with docx2python('path/to/file.docx', 'path/to/image/directory') as docx_content:
    ...

# or

with docx2python('path/to/file.docx') as docx_content:
    docx_content.save_images('path/to/image/directory')

```

__docx_reader__ - a DocxReader (see `docx_reader.py`) instance with several methods for extracting xml portions.


## Arguments

    def docx2python(
        docx_filename: str | Path | BytesIO,
        image_folder: str | None = None,
        html: bool = False,
        paragraph_styles: bool = False,
        extract_image: bool | None = None,
        duplicate_merged_cells: bool = False
    ) -> DocxContent:
        """
        Unzip a docx file and extract contents.

        :param docx_filename: path to a docx file
        :param image_folder: optionally specify an image folder
            (images in docx will be copied to this folder)
        :param html: bool, extract some formatting as html
        :param paragraph_styles: prepend the paragraphs style (if any, else "") to each
            paragraph. This will only be useful with ``*_runs`` attributes.
        :param duplicate_merged_cells: bool, duplicate merged cells to return a mxn
            nested list for each table (default False)
        :return: DocxContent object
        """


## Return Format

Some structure will be maintained. Text will be returned in a nested list, with paragraphs always at depth 4 (i.e., `output.body[i][j][k][l]` will be a paragraph).

If your docx has no tables, output.body will appear as one a table with all content in one cell:

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


A docx document can be tables within tables within tables. Docx2Python flattens most of this to more easily navigate
within the content.

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

    :tables: value could come from, e.g.,
        * docx_to_text_output.document
        * docx_to_text_output.body
    """

    # prepend index tuple to each paragraph
    for (i, j, k, l), paragraph in enum_at_depth(tables, 4):
        tables[i][j][k][l] = " ".join([str((i, j, k, l)), paragraph])

    # wrap each paragraph in <pre> tags
    for (i, j, k), cell in enum_at_depth(tables, 3):
        tables[i][j][k] = "".join(["<pre>{x}</pre>".format(x) for x in cell])

    # wrap each cell in <td> tags
    for (i, j), row in enum_at_depth(tables, 2):
        tables[i][j] = "".join(["<td>{x}</td>".format(x) for x in row])

    # wrap each row in <tr> tags
    for (i,), table in enum_at_depth(tables, 1):
        tables[i] = "".join("<tr>{x}</tr>".format(x) for x in table)

    # wrap each table in <table> tags
    tables = "".join(['<table border="1">{x}</table>'.format(x) for x in tables])

    return ["<html><body>"] + tables + ["</body></html>"]
```

```
>>> tables = [[[['a', 'b'], ['a', 'd']]]]
>>> html_map(tables)
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

Some fine print about checkboxes:

MS Word has checkboxes that can be checked any time, and others that can only be checked when the form is locked.
The previous print as. ``\u2610`` (open checkbox) or ``\u2612`` (crossed checkbox). Which this module, the latter will
too. I gave checkboxes a bailout value of ``----checkbox failed----`` if the xml doesn't look like I expect it to,
because I don't have several-thousand test files with checkboxes (as I did with most of the other form elements).
Checkboxes *should* work, but please let me know if you encounter any that do not.

## access comments

You can access docx comments with the `comments` attribute of the output `DocxContent` object.

```python
with docx2python('path/to/file.docx') as docx_content:
    print(docx_content.comments)
```

For each comment, this will return a tuple:

    `(reference_text, author, date, comment_text)`


# New in docx2python Version 2

## merge consecutive runs with identical formatting

MS Word will break up text runs arbitrarily, often in the middle of a word.


    <w:r>
        <w:t>work to im</w:t>
    </w:r>
    <w:r>
        <w:t>prove docx2python</w:t>
    </w:r>

This makes things like algorithmic search-and-replace problematic. Docx2python does not currently write docx files,
but I often use docx templates with placeholders (e.g., `#CATEGORY_NAME#`) then replace those placeholders with data.
This won't work if your placeholders are broken up (e.g, `#CAT`, `E`, `GORY_NAME#`).

Docx2python v1 merges such runs together when exporting text. Docx2python v2 will merge such runs in the XML as a
pre-processing step. This will allow saving such "repaired" XML later on.

## merge consecutive links with identical hrefs

MS Word will break up links, giving each link a different `rId`, even when these `rIds` point to the same address.

    <w:hyperlink r:id="rId13">  # rID13 points to https://github.com/ShayHill/docx2python
        <w:r>
            <w:t>docx2py</w:t>
        </w:r>
    </w:hyperlink>
    <w:hyperlink r:id="rId14">  # rID14 ALSO points to https://github.com/ShayHill/docx2python
        <w:r>
            <w:t>thon</w:t>
        </w:r>
    </w:hyperlink>

This is similar to the broken-up runs, but the cause is a little deeper in. Docx2python v1 makes a mess of these.

    <a href="https://github.com/ShayHill/docx2python">docx2py</a>
    <a href="https://github.com/ShayHill/docx2python">thon</a>

Docx2python v2 will merge such links together in the XML as a pre-processing step. As above, this will allow saving
such "repaired" XML later on.

## correctly handle nested paragraphs

MS Word will nest paragraphs

    <w:p>
        <w:r>
            <w:t>text</w:t>
        </w:r>
        <w:p>  # paragraph inside a paragraph
            <w:r>
                <w:t>text</w:t>
            </w:r>
        </w:p>
        <w:r>
            <w:t>text</w:t>
        </w:r>
    </w:p>

I haven't been able to create such a paragraph, but I've found a few files that have them. Docx2pyhon v1 will omit
closing html tags when a new paragraph is opened before the old paragraph is closed.

    <b>outer par bold text

    <i>This text is in nested par (not bold)</i>

    outer par bold text</b>

Docx2python v2 will correctly handle such cases, but this will require substantial internal changes to the way
docx2python opens and closes paragraphs.

    <b>outer par bold text</b>

    <i>This text is in nested par (not bold)</i>

    </b>outer par bold text</b>

## paragraph styles

The internal changes allow for easy access to paragraph styles (e.g., `Heading 1`). Docx2python v1 ignores these, even
with `html=True`. Docx2python v2 will capture paragraph styles.

    <h1>h1 is a paragraph style<b>bold is a run style</b></h1>

## export xml

To allow above-described light editing (e.g., search and replace), docx2python v2 will give the user access to

    1. extracted xml files
    2. the functions used to write these files to a docx

The user can only go so far with this. A docx file is built from folders full of xml files. None of these xml
files are self contained. But search and replace is enough to make document templates (documents with placeholders for
data), and that's pretty useful in itself.

## expose some intermediate functionality

Navigating through XML is straightforward with `lxml`. It is a separate step to take whatever you find and bring it
*out* of the XML. For instance, you may want to iterate over a document, looking for paragraphs with a particular
format, then pull the text out of those paragraphs. Docx2python v1 did not separate or expose "iter the document" and
"pull the content". Docx2python v2 separates and exposes these steps. This will allow easier extension.

See the `docx_reader.py` module and simple examples in the `utilities.py` module.

## see utilities.py for examples of major new features.
