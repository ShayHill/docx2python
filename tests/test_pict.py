"""Test functionality with pict elements.

:author: Shay Hill
:created: 1/29/2020

Such file was sent to me by stefan-hock20 on github. Images are referenced in
document.html as

```
<w:pict>
    <v:shape id=Figure 1" o:spid="_x0000_i1085" type="#_x0000_t75"
        style="width:441.6pt;height:264.6pt;visibility:visible">
    <v:imagedata r:id="rId50" o:title=""/></v:shape>
</w:pict>
```

docx2text 1.19 would get the image, but not mark the image location in the output text.
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestPictElement:
    def test_extraction(self) -> None:
        """Image placeholder inserted into extracted text."""
        extraction = docx2python(RESOURCES / "has_pict.docx")
        assert "image1.png" in extraction.images
        assert "----media/image1.png----" in extraction.text
        extraction.close()


class TestPictWithAltText:
    def test_extraction(self) -> None:
        """Image placeholder inserted into extracted text."""
        extraction = docx2python(RESOURCES / "pic_alt_text.docx")
        text = extraction.text
        assert "Alt description" in text
        extraction.close()
