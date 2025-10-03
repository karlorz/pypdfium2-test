# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a macOS-focused PDF to image conversion utility that specializes in rendering PDF files using system STSong fonts for proper Chinese character display. The project uses pypdfium2 for PDF processing and PIL (Pillow) for image output.

## Common Commands

### Environment Setup
```bash
# Sync with local pypdfium2 submodule (REQUIRED first step)
# macOS/Linux
./sync-local-pypdfium2.sh

# Windows
sync-local-pypdfium2.bat

# Install dependencies using uv
uv sync
```

### Running the Converter
```bash
# Convert single page (default: page 1)
python test_pypdfium2.py input/page5.pdf

# Convert with custom output path and DPI
python test_pypdfium2.py input/page5.pdf output.png 300

# Convert all pages to output directory
python test_pypdfium2.py input/page5.pdf --all

# Convert specific page (1-based index)
python test_pypdfium2.py input/page5.pdf output.png 300 0
```

### Development and Testing
```bash
# Run with sample PDF
python test_pypdfium2.py input/page5.pdf --all

# Check output results
ls -la output/

# Re-sync after pypdfium2 submodule changes
./sync-local-pypdfium2.sh  # or sync-local-pypdfium2.bat on Windows
```

### Submodule Development Workflow
```bash
# Work with the pypdfium2 submodule
cd pypdfium2
# Make your changes...
git add . && git commit -m "Your changes" && git push origin main

# Go back to main project - changes are immediately available
cd ..
python test_pypdfium2.py input/page5.pdf  # Uses modified version
```

## Architecture

### Core Components

**PDFConverter Class** (`test_pypdfium2.py`):
- **Font Detection**: Automatically locates macOS STSong fonts using hardcoded paths and system_profiler fallback
- **PDF Processing**: Uses pypdfium2 library for PDF loading and rendering
- **Image Generation**: Converts PDF pages to PNG images with configurable DPI (default 300)

**Font Integration Strategy**:
1. **Primary Search**: Checks standard macOS font locations (`/System/Library/Fonts/Supplemental/Songti.ttc`)
2. **Fallback**: Uses `system_profiler SPFontsDataType` to locate system fonts
3. **Rendering**: Leverages macOS system STSong fonts for Chinese text rendering

**Key Technical Details**:
- Uses `pypdfium2.raw` for direct PDFium API access when needed
- Font detection optimized for macOS environment
- High-DPI rendering with scale factor calculation (DPI/72.0)
- PNG output with embedded DPI information

### Dependencies
- `pypdfium2>=4.30.0`: PDF processing and rendering (local submodule)
- `pillow>=10.0.0`: Image manipulation and output
- `fonttools>=4.60.1`: Font analysis (optional, imported conditionally)
- `pymupdf>=1.26.4`: Alternative PDF processing (present in dependencies but not actively used)

### pypdfium2 Local Submodule
This project uses a local pypdfium2 submodule for custom modifications:

**Configuration** (`pyproject.toml`):
```toml
[tool.uv.sources]
pypdfium2 = { path = "./pypdfium2", editable = true }
```

**Sync Scripts**:
- `sync-local-pypdfium2.sh`: Unix (macOS/Linux) sync script
- `sync-local-pypdfium2.bat`: Windows sync script

**Important Notes**:
- **Always run sync script first** before `uv sync` or development
- Scripts handle GitHub CLI attestation verification automatically
- Local submodule is installed as editable dependency
- Changes in `./pypdfium2/` are immediately available
- See `SYNC_README.md` for detailed sync documentation

## File Structure Notes

### Core Files
- `test_pypdfium2.py`: Main converter implementation (single-file solution)
- `pyproject.toml`: Project configuration with local pypdfium2 source
- `sync-local-pypdfium2.sh`: Unix sync script for GitHub CLI bypass
- `sync-local-pypdfium2.bat`: Windows sync script for GitHub CLI bypass
- `SYNC_README.md`: Detailed sync script documentation

### Data Files
- `input/page5.pdf`: Sample PDF for testing (contains Chinese text requiring STSong fonts)
- `fonts.md`: Reference font mapping information (not used by current implementation)
- `output/`: Generated PNG images (auto-created if missing)

### Submodule
- `pypdfium2/`: Git submodule (your fork) with custom modifications
  - Uses `[tool.uv.sources]` configuration for editable development
  - Requires sync script to handle GitHub CLI attestation issues

## Platform Considerations

This implementation is macOS-specific due to:
- Hardcoded macOS font paths for STSong/Songti fonts
- System_profiler integration for font discovery
- Focus on Chinese character rendering with macOS system fonts

The converter expects macOS system fonts to be available and will fail gracefully if STSong fonts cannot be located.