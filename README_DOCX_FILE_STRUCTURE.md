## typical docx file format

To assist with reading the project documentation or extending `docx2python`.

There are four basic types of files:

    1. _rels/.rels - A list of docx content files (e.g., ``document.xml``)

    2. content files - files that contain the text displayed in the docx. (e.g., ``document.xml``, ``header1.xml``).
       These files reference non-content files (images and formatting specifications) through relId numbers, which are
       defined in content-file rels.

    3. content-file rels - (e.g., ``document.xml.rels``) this is where relId numbers are defined. The relId numbers
       used in ``document.xml`` will be defined in ``document.xml.rels``.

    4. display files - (e.g., ``numbering.xml``) that tell the content files how to display text. These are linked from
       the content files through content-file rels.

### Docx file structure

    + _rels  # named references to data (links, values, etc. for entire document)
        - .rels  # map to locations of major files (e.g., document.xml)

    + customXml  # all ignored by docx2python
        - item1.xml
        - item2.xml
        - item3.xml
        - itemProps1.xml
        - itemProps2.xml
        - itemProps2.xml
        _ _rels
            - item1.xml.rels
            - item2.xml.rels
            - item3.xml.rels

    + docProps
        - app.xml  # ignored by docx2python
        - core.xml  # author, modification date, etc.
        - custom.xml  # ignored by docx2python

    + word  # content of docx
        + _rels  # images, numbering formats, etc. for content xml files
            - document.xml.rels
            - header1.xml.rels
            - header2.xml.rels
            - header3.xml.rels
        + media  # folder holding all pictures attached in the docx file
            - image1.jpg
            - image2.jpg
        + theme  # ignored by docx2python
            - theme1.xml
        - document.xml  # main body text
        - header1.xml  # header 1 content
        - footer1.xml
        - footnotes.xml
        - fontTable.xml  # "long-hand" font descriptions. Ignored by docx2python
        - numbering.xml  # required data to auto number paragraphs. doxc2python reads this
        - settings.xml  # global file specifications. Ignored by docx2python
        - styles.xml # table styles, etc. Ignored by docx2python
        - webSettings.xml  # ignored by docx2python

A ``*.docx`` file is just a zipped up file structure (the structure defined above). You can unzip a docx file, make changes, then zip it back up and everything will work (provided your changes are valid xml).
