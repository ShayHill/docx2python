#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Test corrections for google docs docx files

:author: Shay Hill
:created: 11/2/2020

File `test-docx2python-conversion-google_docs.docx` sent by a user.

Traceback (most recent call last):
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/bin/word2md", line 33, in
sys.exit(load_entry_point('word2md', 'console_scripts', 'word2md')())
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/lib/python3.8/site-packages/click/core.py", line 829, in call
return self.main(*args, **kwargs)
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/lib/python3.8/site-packages/click/core.py", line 782, in main
rv = self.invoke(ctx)
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/lib/python3.8/site-packages/click/core.py", line 1066, in invoke
return ctx.invoke(self.callback, **ctx.params)
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/lib/python3.8/site-packages/click/core.py", line 610, in invoke
return callback(*args, **kwargs)
File "/Users/cyee/projects/python/word-to-md/word2md.py", line 349, in cli
make_md_from_entire_doc(path)
File "/Users/cyee/projects/python/word-to-md/word2md.py", line 300, in make_md_from_entire_doc
document = docx2python(input_file, html=True)
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/lib/python3.8/site-packages/docx2python/main.py", line 35, in docx2python
context = get_context(zipf)
File "/Users/cyee/.local/share/virtualenvs/word-to-md-EFw2UvDn/lib/python3.8/site-packages/docx2python/docx_context.py", line 272, in get_context
"docProp2text": collect_docProps(zipf.read("docProps/core.xml")),
File "/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/python3.8/zipfile.py", line 1475, in read
with self.open(name, "r", pwd) as fp:
File "/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/python3.8/zipfile.py", line 1514, in open
zinfo = self.getinfo(name)
File "/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/python3.8/zipfile.py", line 1441, in getinfo
raise KeyError(
KeyError: "There is no item named 'docProps/core.xml' in the archive"

"""

from pathlib import Path

from docx2python import docx2python

TEST_FILE = Path(
    __file__, "..", "resources", "test-docx2python-conversion-google_docs.docx"
)


class TestGoogleDocs:
    def test_empty_properties_dict_if_docProps_not_found(self) -> None:
        """
        It seems Google Docs docx files to not contain a document properties file:
        `docProps/core.xml`. The contents of this file are returned as a dictionary.
        To correct the above error, result.properties will now return an empty
        dictionary.
        """
        result = docx2python(TEST_FILE)
        assert result.properties == {}
