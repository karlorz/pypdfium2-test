#!/usr/bin/env python3

# Import pypdfium2 helpers
from pypdfium2._helpers.document import PdfDocument

def main():
    # Open the PDF document
    pdf = PdfDocument("input/page5.pdf")

    # Render first page
    page = pdf[0]
    bitmap = page.render(scale=2.0)  # 2x scale for good quality
    image = bitmap.to_pil()
    image.save("output/page5_page_1.png")

    print("PDF page converted successfully!")
    print(f"Page rendered at {bitmap.width}x{bitmap.height} pixels")

if __name__ == "__main__":
    main()