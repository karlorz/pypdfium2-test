#!/usr/bin/env python3
"""
Simple PDF to Image Converter
Basic conversion using default pypdfium2 settings
"""

import sys
import os
from PIL import Image
import pypdfium2 as pdfium


class PDFConverter:
    """Simple PDF to PNG converter"""

    def __init__(self):
        self.pdf = None

    def load_pdf(self, pdf_path):
        """Load PDF file"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        self.pdf = pdfium.PdfDocument(pdf_path)
        return len(self.pdf)

    def convert_to_image(self, pdf_path, output_path=None, dpi=150, page=0):
        """Convert PDF page to PNG image"""
        try:
            # Load PDF if not already loaded
            if not self.pdf or (hasattr(self.pdf, 'name') and self.pdf.name != pdf_path):
                page_count = self.load_pdf(pdf_path)
            else:
                page_count = len(self.pdf)

            if page < 0 or page >= page_count:
                raise ValueError(f"Invalid page {page}. PDF has {page_count} pages.")

            # Get page
            pdf_page = self.pdf[page]

            # Render with DPI scale
            scale = dpi / 72.0
            bitmap = pdf_page.render(scale=scale, rotation=0)

            # Convert to PIL Image
            image = bitmap.to_pil()

            # Generate output path if not provided
            if not output_path:
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_path = os.path.join(output_dir, f"{pdf_name}_page_{page + 1}.png")

            # Save image
            image.save(output_path, dpi=(dpi, dpi))

            return output_path

        except Exception as e:
            print(f"❌ Error converting {pdf_path}: {e}")
            return None

    def convert_all_pages(self, pdf_path, output_dir="output", dpi=150):
        """Convert all PDF pages to PNG images"""
        try:
            page_count = self.load_pdf(pdf_path)
            os.makedirs(output_dir, exist_ok=True)

            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            converted_files = []

            for page_num in range(page_count):
                output_path = os.path.join(output_dir, f"{pdf_name}_page_{page_num + 1}.png")
                result = self.convert_to_image(pdf_path, output_path, dpi, page_num)
                if result:
                    converted_files.append(result)
                    print(f"✓ Page {page_num + 1}/{page_count}: {os.path.basename(result)}")

            return converted_files

        except Exception as e:
            print(f"❌ Error converting {pdf_path}: {e}")
            return []


def main():
    """Main function - Simple PDF to PNG conversion"""
    if len(sys.argv) < 2:
        print("Simple PDF to PNG Converter")
        print("Usage: python simple_pdf_to_image.py <pdf_file> [output_path] [dpi] [page_number]")
        print("")
        print("Examples:")
        print("  python simple_pdf_to_image.py input/document.pdf")
        print("  python simple_pdf_to_image.py input/document.pdf output.png 150")
        print("  python simple_pdf_to_image.py input/document.pdf output.png 150 0")
        print("  python simple_pdf_to_image.py input/document.pdf --all [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Parse arguments
    output_path = None
    dpi = 150
    page = 0
    convert_all = False
    output_dir = "output"

    if len(sys.argv) > 2:
        if sys.argv[2] == '--all':
            convert_all = True
            output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
        else:
            custom_output = sys.argv[2]
            if os.path.isabs(custom_output):
                output_path = custom_output
            else:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, custom_output)

            if len(sys.argv) > 3:
                try:
                    dpi = int(sys.argv[3])
                    if len(sys.argv) > 4:
                        page = int(sys.argv[4]) - 1
                except ValueError:
                    dpi = 150

    # Initialize converter
    converter = PDFConverter()

    # Convert PDF
    if convert_all:
        print(f"🖼️ Converting all pages to {output_dir}/...")
        converted_files = converter.convert_all_pages(pdf_path, output_dir, dpi)
        if converted_files:
            print(f"✅ Successfully converted {len(converted_files)} pages to {os.path.abspath(output_dir)}")
        else:
            print("❌ No pages were converted")
    else:
        print(f"🖼️ Converting to PNG (DPI: {dpi})...")
        result = converter.convert_to_image(pdf_path, output_path, dpi, page)

        if result:
            print(f"✅ Successfully converted to {os.path.abspath(result)}")
            # Show image info
            img = Image.open(result)
            print(f"📐 Size: {img.size} pixels")
            print(f"📐 DPI: {dpi}")
        else:
            print("❌ Conversion failed")


if __name__ == "__main__":
    main()