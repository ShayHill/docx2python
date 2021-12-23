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

--  Join run elements internally when docx2python cannot differentiate style.

If you've ever unzipped a docx file and searched for a word in your document, you probably didn't find it. This is because MSWord splits continuous text into smaller runs if the runs differ in spell-check accuracy, revision time, and other characteristics docx2python does not extract. This makes it hard to, for instance, search and replace text in the xml. Docx2Python v2 reads through the xml and joins such runs as a pre-processing step. This greatly simplifies searching output for formatted text. This will allow search and replace and other light xml operations in the future. Runs with different formatting are not joined, even if html=False is set.

--  Return text split into paragraphs (as previous version) or runs (new to Docx2Python v2).

The previous header, footer, body, footnotes, and endnotes attributes returned docx content as a 4-deep nested list of paragraph text. (paragraphs as strings): ``[[[["This is a paragraph"]]]]``. These attributes are still available. New attributes header_runs, footer_runs, etc. return docx content as a 5-deep nested list of run strings (paragraphs as lists of strings): ``[[[[['This' , ' is a ', 'paragraph']]]]]``

--  No more nested HTML styles.

Docx2Python v1 would simplify html tags: ``<b>bold text <i>bold-italic</i> more bold text</b>``. This makes an attractive export, but complicates searching / filtering for formatted text.

Docx2Python v2 will not nest html tags: ``<b>bold text </b><b><i>bold-italic</i></b><b> more bold text</b>``.

``_runs`` attributes will return ``[<b>"bold text </b>", "<b><i>bold-italic</i></b>", "<b> more bold text</b>]``.

--  More html run styles.

Now supports ``<i>``italic, ``<b>``bold, ``<u>``underline, ``<s>``strike, ``<sup>``superscript, ``<sub>``subscript, ``<span style="font-variant: small-caps">``small caps, ``<span style="text-transform:uppercase">``all caps, ``<span style="background-color: yellow">``highlighted, ``<span style="font-size:32">``font size, ``<span style="color:#ff0000">``colored text.

This is extensible. Styles can be added and removed. Note that the style change for font size has been updated from ``<font size="32">`` to ``<span style="font_size:32">`` to eliminate deprecated ``font`` elements. (Thank you, user raiyankamal, for pointing this out.)

--  Slightly more structure is preserved (more empty sublists and strings).

Docx2Python v1 assumed a document was a series of tables and formatted output that way: ``[body[table[table_row[table_cell[paragraph``

Simple docx files *are* structured this way, but there are elements (e.g., ``<w:footnotes>``, ``<w:footnote>``) that act like tables without being exactly tables. Docx2Python v2 treats any element 1-level above a paragraph as a table cell, any element 2-levels above a paragraph as a table row, etc. The upshot of this is that there will be more whitespace in your exports. This whitespace is potentially useful information, but you can easily filter it out if you don't need it.

--  No longer supports Python 3.4, 3.5, or 3.6

Now only supports Python 3.7+

--  XML and other information from an unzipped docx file now available as a DocxReader instance.

Docx2Python v1 extracted xml from a zip file and passed it straight to formatting functions. Docx2Python v2 takes an intermediate step: hold the xml and inferred attributes of the input docx in DocxContext and File instances. These allow a view into the xml for users who are comfortable working that way. A user can now execute search&replace and other simple operations before extracting the text. Here's an example:

    def replace_root_text(root: etree._Element, old: str, new: str) -> None:
    """Replace :old: with :new: in all descendants of :root:

        :param root: an etree element presumably containing descendant text elements
        :param old: text to be replaced
        :param new: replacement text
        """
        for text_elem in (x for x in root.iter() if x.text):
            text_elem.text = (text_elem.text or "").replace(old, new)


    def replace_docx_text(
        path_in: Union[Path, str],
        path_out: Union[Path, str],
        *replacements: Tuple[str, str],
        html: bool = False
    ) -> None:
    """Replace text in a docx file.

        :param path_in: path to input docx
        :param path_out: path to output docx with text replaced
        :param replacements: tuples of strings (a, b) replace a with b for each in docx.
        :param html: respect formatting (as far as docx2python can see formatting)
        """
        reader = docx2python(path_in, html=html).docx_reader
        for file in reader.content_files():
            root = file.root_element
            for replacement in replacements:
                replace_root_text(root, *replacement)
        reader.save(path_out)
        return

--  Save altered xml

A user can extract the xml, alter it, and save the resulting docx. This will be simpler than accomplishing the same with just lxml, because

1. consecutive runs with identical styles will be merged (no more attempting search and replace with "wo" "rds" " brok" "en" " in" "to" "multiple runs".)
2. some of the file structure will be available.
3. Docx2Python will find all content files and return them as a list as DocxContext.content_files.

TODO: code an example for this functionality


-- Soft line breaks are now exported as `'\n'`

Docx2Python v1 ignored soft line breaks. These are represented in the xml as `<w:br/>`. Docx2Python v2 exports these as `'\n'`.

-- Now recognizes math text.

Equations in Word are made up internally of ``<w:m>`` elements. Previous versions of Docx2Python ignored these elements. These are now recognized.

Equations in Word's Professional format will return garbage (a smattering of text elements inside an equation).

Equations in Word's Inline format will return valid LaTeX (e.g., ``'\\int_{0}^{1}x'``).

-- Now works with LibreOffice conversions

User shadowmimosa reported that docx files converted by LibreOffice from docx raised a CaretDepthError. This files now extract without error.

-- New option `paragraph_styles=True` will append a paragraph style as the first run of each paragraph. These will often be "None", but may be a "Header", "Footnote" or similar. These can be used for factoring extracted paragraphs. See `utilities.py` for example usage.

-- Replace `&` with `&amp` when exporting html styles

Docx2Python v1 did not replace `&`

---- version 2.0.1 - small import bug fix

---- version 2.0.2 - math equations now wrapped in `<latex></latex>`. Thank you, usr3
