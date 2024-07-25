""" Test corrections for google docs docx files

:author: Shay Hill
:created: 11/2/2020

Docx files created in MS Work have a ``docProps.xml`` file with author, etc.
Docx files created in google docs do not have a ``docProps.xml`` file.

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

import pytest

from docx2python import docx2python
from tests.conftest import RESOURCES

FILE_WITH_DOCPROPS = RESOURCES / "example.docx"

FILE_WITHOUT_DOCPROPS = RESOURCES / "test-docx2python-conversion-google_docs.docx"


class TestDeprecatedPropertiesProperty:
    def test_deprecated_properties_property(self) -> None:
        """
        Raise a future warning when user requests ``result.properties``
        """
        with docx2python(FILE_WITH_DOCPROPS) as result:
            with pytest.warns(FutureWarning):
                _ = result.properties


class TestDocPropsFound:
    def test_docprops_found(self) -> None:
        """
        Return docProps as a dictionary
        """
        with docx2python(FILE_WITH_DOCPROPS) as result:
            assert result.core_properties == {
                "created": "2019-07-05T21:51:00Z",
                "creator": "Shay Hill",
                "description": None,
                "keywords": None,
                "lastModifiedBy": "Shay Hill",
                "modified": "2021-03-26T00:30:00Z",
                "revision": "7",
                "subject": None,
                "title": None,
            }


class TestGoogleDocs:
    def test_empty_properties_dict_if_docProps_not_found(self) -> None:
        """
        It seems Google Docs docx files to not contain a document properties file:
        `docProps/core.xml`. The contents of this file are returned as a dictionary.
        To correct the above error, result.properties will now return an empty
        dictionary (with a warning).
        """
        with docx2python(FILE_WITHOUT_DOCPROPS) as result:
            with pytest.warns(UserWarning):
                assert result.core_properties == {}
