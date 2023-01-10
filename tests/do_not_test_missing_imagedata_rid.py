"""Skip image element when imagedata r:id cannot be found.

:author: Shay Hill
:created: 11/15/2020

User forky2 sent a docx file with an empty imagedata element:

`<v:imagedata croptop="-65520f" cropbottom="65520f"/>`

Docx2python expects to encounter

`<v:imagedata r:id="rId689" o:title=""/>`

Where `r:id="rId689"` is mapped to an image filename in one of the `rels` files.

The missing `r:id` raises a KeyError in docx2python v1.27

```
    Traceback (most recent call last):
      File "./process.py", line 99, in <module>
        process_zip("Specs/2020-06/Rel-16/25_series/25101-g10.zip")
      File "./process.py", line 70, in process_zip
        doc_data = docx2python(docx_file)
      File "/home/forky2/projects/docx2python/docx2python/main.py", line 61, in docx2python
        body = file_text(context["officeDocument"])
      File "/home/forky2/projects/docx2python/docx2python/main.py", line 56, in file_text
        return get_text(unzipped, context)
      File "/home/forky2/projects/docx2python/docx2python/docx_text.py", line 264, in get_text
        branches(ElementTree.fromstring(xml))
      File "/home/forky2/projects/docx2python/docx2python/docx_text.py", line 248, in branches
        branches(child)
      File "/home/forky2/projects/docx2python/docx2python/docx_text.py", line 248, in branches
        branches(child)
      File "/home/forky2/projects/docx2python/docx2python/docx_text.py", line 248, in branches
        branches(child)
      [Previous line repeated 2 more times]
      File "/home/forky2/projects/docx2python/docx2python/docx_text.py", line 239, in branches
        rId = child.attrib[qn("r:id")]
    KeyError: '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
```

Solution: skip silently when an `r:id` cannot be found for an `imagedata` element.
"""

# from docx2python import docx2python


# class TestMissingRIdInImagedata:
# def test_skips_missing_rid(self) -> None:
# """Silently skip over imagedata element if r:id not found"""
# pars = docx2python("resources/imagedata_without_rid.docx")
