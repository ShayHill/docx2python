---- version 1.25 - 200820 Added support for Table of Contents text

A docx table of contents is built like a set of hyperlinks, with each hyperlink element's having an anchor (internal link) instead of an href (external link).

Previously any document with a Table of Contents would fail with `KeyError: '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'` after failing to find an href. Now, docx2python will continue without warning if an href is not found in a hyperlink element. In an href is found, docx2python will print the href inside `<a href="{}">` as before. Anchor (internal link) elements are meaningless outside the docx and are therefore ignored by docx2python.


---- version 1.26 - 201005 Continue (with bullet) when numbering-format lookup fails

Some documents created in Pages use a different indexing scheme to specify numbered-list formats and values. I cannot infer formats or values from such files without potentially changing existing behavior. The previous behavior in such cases was to fail with an IndexError. v1.26 will now replace any numbering format with a "bullet" (--) when the format or value cannot be inferred.

This will only happen where the program would previously have failed with an IndexError, so no previous behavior (which allowed the program to complete) has been altered.


---- version 1.27 - 201102 Continue when document properties are not found

`docx2python(file).properties` returns a dictionary of document properties (e.g., {'Author': 'Shay Hill'}). Google Docs (and perhaps others) do not store such properties. When document properties cannot be found, v1.27 will continue and return an empty dictionary for `docx2python(file).properties`.

This will only happen where the program would previously have failed with a KeyError, so no previous behavior (which allowed the program to complete) has been altered.


---- version 1.27.1 - 201115 Continue when image r:id is not found

A user found a docx `imagedata` element with a missing `r:id` element. The `r:id` number gives the location of an image filename. I presume this `imagedata` element is a vector graphic, which `docx2python` does not and will not support. This makes two out of three `r:id` lookup positions (`hyperlink`, `image`, and `imagedata`) for which users have found absent `r:id`. None so far have contained anything meaningful for text export (internal links in a previous case and vector graphics in this case). Now all `r:id` lookups take place within `suppress(KeyId)` context.

This will only happen where the program would previously have failed with a KeyError, so no previous behavior (which allowed the program to complete) has been altered.


---- version 2.0.0 - big changes

--  Join runs internally when docx2python cannot differentiate style.

MSWord will split continuous text into smaller runs if the runs differ in spell-check accuracy, revision time, and other characteristics docx2python does not extract. This makes it hard to, for instance, search and replace text in the xml. Docx2Python v2 reads through the xml and joins such runs as a pre-processing step. This greatly simplifies searching output for formatted text. This will allow search and replace and other light xml operations in the future. Runs with different formatting are not joined, even if html=False is set.

--  Return text split into paragraphs (as previous version) or runs (new to Docx2Python v2).

The previous header, footer, body, footnotes, and endnotes attributes returned docx content as a 4-deep nested list of paragraph text. (paragraphs as strings): ``[[[["This is a paragraph"]]]]``. These attributes are still available. New attributes header_runs, footer_runs, etc. return docx content as a 5-deep nested list of run strings (paragraphs as lists of strings): ``[[[[['This' , ' is a ', 'paragraph']]]]]``

--  No more nested HTML styles.

Docx2Python v1 would simplify html tags: ``<b>bold text <i>bold-italic</i> more bold text</b>``. This makes an attractive export, but complicates searching / filtering for formatted text.

Docx2Python v2 will not nest html tags: ``<b>bold text </b><b><i>bold-italic</i></b><b> more bold text</b>``.

``_runs`` attributes will return ``[<b>"bold text </b>", "<b><i>bold-italic</i></b>", "<b> more bold text</b>]``.

--  More html run styles.

Now supports ``<i>``italic, ``<b>``bold, ``<u>``underline, ``<s>``strike, ``<sup>``superscript, ``<sub>``subscript, ``<font style="font-variant: small-caps">``small caps, ``<font style="text-transform:uppercase">``all caps, ``<span style="background-color: yellow">``highlighted, ``<font style="font-size:32">``font size, ``<font style="color:#ff0000">``colored text.

This is extensible. Styles can be added and removed. Note that the style change for font size has been updated from ``<font size="32">`` to ``<font style="font_size:32">``

--  Slightly more structure is preserved (more empty sublists and strings).

Docx2Python v1 assumed a document was a series of tables and formatted output that way: ``[body[table[table_row[table_cell[paragraph``

Simple docx files *are* structured this way, but there are a elements (e.g., ``<w:footnotes>``, ``<w:footnote>``) that act like tables without being exactly tables. Docx2Python v2 treats any element 1-level above a paragraph as a table cell, any element 2-levels above a paragraph as a table row, etc. The upshot of this is that there will be more whitespace in your exports. This whitespace is potentially useful information, but you can easily filter it out if you don't need it.

--  No longer supports Python 3.4 or 3.5

Now only supports Python 3.6+

--  XML and other information from an unzipped docx file now available as a DocxContext instance.

Docx2Python v1 extracted xml from a zip file and passed it straight to formatting functions. Docx2Python v2 takes an intermediate step: hold the xml and inferred attributes of the input docx in DocxContext and File instances. These allow a view into the xml for users who are comfortable working that way. A user can now execute search&replace and other simple operations before extracting the text. 