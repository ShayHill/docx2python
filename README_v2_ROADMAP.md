# docx2python Version 2 roadmap

I created docx2python to strip *content* from docx files. However, I sometimes finding myself wanting information that
isn't *exactly* content: most frequently paragraph and text styles. You can do a lot more with document content when you
can see the difference between headings and text.

Docx2python v1 extracts some of that information. It adds plain text tags to show where the footers, headers, footnotes,
etc. end up in the extracted text. It's not comprehensive, but it is simple.

On the other end of the spectrum, one can navigate directly through the XML and have access to *all* information in the
file. That's simple too until you want to get whatever you find out of the XML.

Docx2python v2 will take a few steps into the intermediate space between these two options.

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
closing htms tags when a new paragraph is opened before the old paragraph is closed.

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

## write docx files

There are no plans for docx2python to build the file structure of a docx document and create it from a Python data
structure. That wouldn't be a difficult project, but docx2python is focused on getting information OUT OF docx files.

That being said, docx2python has 99% of everything you'd need to lightly edit a docx file and re-save it.
Docx2python 2.0 will be able to export docx with merged links and runs (as above).

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
"pull the content". Docx2python v2 will separate and expose these steps. That will allow easier extension.