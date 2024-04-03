"""Test functions in docx2python.namespace.py

:author: Shay Hill
:created: 7/5/2019
"""

from docx2python.namespace import NSMAP, qn


class TestQn:
    def test_qn(self) -> None:
        """Similar to test from docstring.

        `qn('p:cSld')`` returns ``'{http://schemas.../main}cSld'`
        """
        assert qn("w:p") == "{{{}}}p".format(NSMAP["w"])
