"""User K Ravikiran had trouble with long hyperlinks.

The sample file here has a hyperlink he was not able to export correctly.

:author: Shay Hill
:created: 2024-01-20
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES

long_hyperlink = RESOURCES / "long_hyperlink.docx"


class TestLongHyperlink:
    def test_non_html(self) -> None:
        """Exports full hyperlink without html flag."""
        with docx2python(long_hyperlink) as docx_content:
            extracted_text = docx_content.text
        long_url = (
            "https://connect.asdfg.com/wikis/home?lang-en-us"
            + "#!/wiki/asdfasdf_asdfasdf/page/EOL%20support%20-%20MDGI"
        )
        assert long_url in extracted_text

    def test_html(self) -> None:
        """Exports full hyperlink with html flag."""
        with docx2python(long_hyperlink, html=True) as docx_content:
            extracted_text = docx_content.text
        long_url = (
            "https://connect.asdfg.com/wikis/home?lang-en-us"
            + "#!/wiki/asdfasdf_asdfasdf/page/EOL%20support%20-%20MDGI"
        )
        assert long_url in extracted_text
