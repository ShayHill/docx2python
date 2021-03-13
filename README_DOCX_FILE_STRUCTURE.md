## typical docx file format

To assist with reading the project documentation or extending `docx2python`.

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
        - custom.xml  # ignored by docx to python

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


    

