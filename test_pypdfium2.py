  # Direct import (recommended)
from pypdfium2._library_scope import initialize_with_fonts
from pypdfium2._helpers.document import PdfDocument

# Initialize with local FreeType fonts
font_paths = [
    "/System/Library/Fonts/Supplemental/Songti.ttc"  # For Chinese
]

initialize_with_fonts(font_paths)

# Use pypdfium2 normally - it will now use your local fonts
pdf = PdfDocument("input/page5.pdf")
page = pdf[0]
bitmap = page.render(scale=2.0)
image = bitmap.to_pil()
image.save("output/page5_page_1.png")