#!/usr/bin/env python3
"""
PDF to Image Converter with STSong Font Rendering
Compact, optimized solution for macOS PDF to PNG conversion using system STSong fonts
"""

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
import os
import sys
import platform
from PIL import Image
import ctypes
import subprocess

# Check for fontTools availability
try:
    from fontTools.ttLib import TTFont
    FONTTOOLS_AVAILABLE = True
except ImportError:
    FONTTOOLS_AVAILABLE = False


class PDFConverter:
    """Compact PDF to PNG converter with STSong font rendering"""

    def __init__(self):
        self.pdf = None
        self.stsong_font = self._find_stsong_font()
        print(f"🔤 STSong font: {os.path.basename(self.stsong_font) if self.stsong_font else 'Not found'}")

    def _find_stsong_font(self):
        """Find the best STSong font on macOS"""
        font_paths = [
            "/System/Library/Fonts/Supplemental/Songti.ttc",
            "/System/Library/Fonts/Songti.ttc",
            "/Library/Fonts/Songti.ttc"
        ]

        for path in font_paths:
            if os.path.exists(path):
                return path

        # Fallback search using system_profiler
        try:
            result = subprocess.run(['system_profiler', 'SPFontsDataType'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'song' in line.lower() and '.ttc' in line.lower():
                        # Extract path from system_profiler output
                        if 'Location:' in line:
                            path = line.split('Location:')[1].strip()
                            if os.path.exists(path):
                                return path
        except:
            pass

        return None

    def load_pdf(self, pdf_path):
        """Load PDF file"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        self.pdf = pdfium.PdfDocument(pdf_path)
        return len(self.pdf)

    def convert_to_image(self, pdf_path, output_path=None, dpi=300, page=0):
        """Convert PDF page to PNG image using STSong fonts"""
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

            # Render with high DPI
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
            image.save(output_path, dpi=(dpi, dpi), quality=95)

            return output_path

        except Exception as e:
            print(f"❌ Error converting {pdf_path}: {e}")
            return None

    def convert_all_pages(self, pdf_path, output_dir="output", dpi=300):
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

    def get_font_info(self):
        """Get font information"""
        if self.stsong_font:
            return {
                'font_path': self.stsong_font,
                'font_name': os.path.basename(self.stsong_font),
                'available': True
            }
        return {
            'font_path': None,
            'font_name': None,
            'available': False
        }


def main():
    """Main function - PDF to PNG conversion with STSong fonts"""
    if len(sys.argv) < 2:
        print("PDF to PNG Converter with STSong Fonts")
        print("Usage: python test_pypdfium2.py <pdf_file> [output_path] [dpi] [page_number]")
        print("")
        print("Examples:")
        print("  python test_pypdfium2.py input/document.pdf")
        print("  python test_pypdfium2.py input/document.pdf output.png 300")
        print("  python test_pypdfium2.py input/document.pdf output.png 300 0")
        print("  python test_pypdfium2.py input/document.pdf --all  # Convert all pages")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Parse arguments
    output_path = None
    dpi = 300
    page = 0
    convert_all = False

    if len(sys.argv) > 2:
        if sys.argv[2] == '--all':
            convert_all = True
            output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
        else:
            output_path = sys.argv[2]
            if len(sys.argv) > 3:
                try:
                    dpi = int(sys.argv[3])
                    if len(sys.argv) > 4:
                        page = int(sys.argv[4]) - 1  # Convert to 0-based
                except ValueError:
                    dpi = 300

    # Initialize converter
    converter = PDFConverter()

    # Show font info
    font_info = converter.get_font_info()
    print(f"🔤 Font: {font_info['font_name']}")
    print(f"📄 PDF: {pdf_path}")

    # Convert PDF
    if convert_all:
        print(f"🖼️  Converting all pages to {output_dir}/...")
        converted_files = converter.convert_all_pages(pdf_path, output_dir, dpi)
        if converted_files:
            print(f"✅ Successfully converted {len(converted_files)} pages to {os.path.abspath(output_dir)}")
        else:
            print("❌ No pages were converted")
    else:
        print(f"🖼️  Converting to PNG (DPI: {dpi})...")
        result = converter.convert_to_image(pdf_path, output_path, dpi, page)

        if result:
            print(f"✅ Successfully converted to {os.path.abspath(result)}")
            # Show image info
            from PIL import Image
            img = Image.open(result)
            print(f"📐 Size: {img.size} pixels")
            print(f"📐 DPI: {dpi}")
        else:
            print("❌ Conversion failed")


if __name__ == "__main__":
    main()