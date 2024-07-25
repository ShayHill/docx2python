"""Make sure from docx2python import ... works

:author: Shay Hill
:created: 7/17/2019

"""

from docx2python import docx2python
from tests.conftest import RESOURCES


def test() -> None:
    """Just making sure the import works."""
    with docx2python(RESOURCES / "example.docx") as _:
        pass
