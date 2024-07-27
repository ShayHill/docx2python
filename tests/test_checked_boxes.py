""" Identify checked boxes in user-submitted file

:author: Shay Hill
:created: 2021-12-17

From user PandaJones:

'''
Word docx's xml (i believe this is cause the docx version is pretty old) deletes
w:val when the checkbox is checked and has w:val = 0 when the checkbox isn't checked.

This causes a problems that the library defaults to 0 when w:val isn't found in
w:checked. To fix this, I just checked if there is anything attributes in w:check and
return a 1 if there isn't anything there.

I can probably edit the code to check if w:val exist instead as I don't know if
w:checked can have other attributes.

Thank for have this library be able to display checkboxes, it is super useful when
parsing through forms that have all of their stuff in tables.
'''
"""

from docx2python import docx2python
from docx2python.iterators import iter_at_depth
from tests.conftest import RESOURCES


def test_checked_boxes_explicit() -> None:
    """
    The following text boxes are checked. Remaining checkboxes are unchecked.

    Adult Protective Services
    Older Adult Mental Health
    ProsecutorΓÇÖs Office
    Regional Center

    Coroner/Medical Examiner
    Law Enforcement
    Civil Attorney/Legal Services
    Psychologist

    Medical Practitioner
    LTC Ombudsman
    Public Guardian
    Other (describe):

    """
    pars = docx2python(RESOURCES / "checked_boxes.docx", duplicate_merged_cells=False)
    expect: list[list[list[list[str]]]] = [
        [
            [["\u2612", " Adult Protective Services"]],
            [[]],
            [["\u2612", " Older Adult Mental Health"]],
            [[]],
            [[]],
            [[]],
            [["\u2612", " Prosecutor’s Office"]],
            [[]],
            [[]],
            [[]],
            [["\u2612", " Regional Center"]],
            [[]],
        ],
        [
            [["\u2612", " Coroner/Medical Examiner"]],
            [[]],
            [["\u2612", " Law Enforcement"]],
            [[]],
            [[]],
            [[]],
            [["\u2612", " Civil Attorney/Legal Services"]],
            [[]],
            [[]],
            [[]],
            [["\u2612", " Psychologist"]],
            [[]],
        ],
        [
            [["\u2612", " Medical Practitioner"]],
            [[]],
            [["\u2612", " LTC Ombudsman"]],
            [[]],
            [[]],
            [[]],
            [["\u2612", " Public Guardian"]],
            [[]],
            [[]],
            [[]],
            [["\u2612", " Other (describe):\u2002\u2002\u2002\u2002\u2002"]],
            [[]],
        ],
    ]

    assert pars.body_runs[0][3:6] == expect
    pars.close()


def test_unchecked_boxes() -> None:
    """
    The following text boxes are checked. Remaining checkboxes are unchecked.

    Adult Protective Services
    Older Adult Mental Health
    ProsecutorΓÇÖs Office
    Regional Center

    Coroner/Medical Examiner
    Law Enforcement
    Civil Attorney/Legal Services
    Psychologist

    Medical Practitioner
    LTC Ombudsman
    Public Guardian
    Other (describe):

    All other checkboxes are unchecked

    """
    pars = docx2python(RESOURCES / "checked_boxes.docx", duplicate_merged_cells=False)
    all_text = "".join(iter_at_depth(pars.text, 5))
    assert all_text.count("\u2612") == 12
    assert all_text.count("\u2610") == 32
    pars.close()


def test_checkboxes_true_false() -> None:
    """
    Checkboxes with "true" and "false" instead of "1" and "0" values.
    """
    with docx2python(RESOURCES / "checked-true-false.docx") as pars:
        all_text = "".join(iter_at_depth(pars.text, 5))
    assert all_text.count("\u2612") == 4
    assert all_text.count("\u2610") == 4
