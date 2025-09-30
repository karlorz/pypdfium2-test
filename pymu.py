import fitz  # Requires PyMuPDF library: pip install PyMuPDF

def extract_font_info(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        print(f"Fonts on page {page_num + 1}:")
        page = doc[page_num]

        # Get fonts using get_fonts with full=True to get more detailed information
        fonts = page.get_fonts(full=True)
        for font_info in fonts:
            # font_info tuple structure: (xref, ext, type, name, basefont, encoding, referencer)
            xref = font_info[0]
            font_ext = font_info[1]
            ftype = font_info[2]
            name = font_info[3]
            basefont = font_info[4]
            encoding = font_info[5] if len(font_info) > 5 else "Unknown"

            # Get the actual system font name that would be used for rendering
            # The 'name' field from font_info already contains the actual font name
            # that the system font resolver will use
            actual_system_font = name

            # For embedded fonts, try to get more specific information
            if xref > 0:
                try:
                    font_name, font_ext, _, _ = doc.extractFont(xref)
                    if font_name and font_name != "n/a":
                        # Clean up font name by removing subset prefix if present
                        clean_font_name = font_name
                        if '+' in font_name:
                            clean_font_name = font_name.split('+', 1)[1]
                        actual_system_font = clean_font_name

                        # Add file extension information if available
                        if font_ext and font_ext != "n/a":
                            actual_system_font += f" ({font_ext.upper()})"
                except:
                    # If extractFont fails, we still have the name field
                    pass

            # Add encoding information for Type0 fonts which often use CJK encodings
            if ftype == "Type0" and encoding:
                if "GB" in encoding or "UTF16" in encoding:
                    actual_system_font += " [CJK]"
                elif "Identity" in encoding:
                    actual_system_font += " [Identity-H]"

            print(f"## {name}")
            print(f"Type: {ftype}{( '(ClD)' if 'CID' in ftype else '' )}")
            print(f"Encoding: {encoding}")
            print(f"Actual Font: {actual_system_font}")
            print(f"Object Number: {xref}")
            print()
    doc.close()

# Usage
extract_font_info("input/page5.pdf")