# PDF OCR Diff CLI

A command-line tool that compares two PDFs page-by-page using OCR, extracts text with spatial location data (bounding boxes), and generates structured JSON output mapping differences back to page coordinates.

## Features

- **Page-by-page comparison**: Compares PDFs at the page level rather than flattening documents
- **Spatial awareness**: Tracks bounding box coordinates for all text differences
- **OCR-based**: Uses Tesseract OCR to extract text from PDF images
- **Structured output**: Generates machine-readable JSON with difference details
- **Handles unequal documents**: Properly compares PDFs with different page counts

## System Dependencies

Before installing the Python package, you need these system-level dependencies:

### macOS
```bash
brew install poppler tesseract
```

### Linux (Debian/Ubuntu)
```bash
sudo apt-get install poppler-utils tesseract-ocr
```

### Linux (Fedora/CentOS)
```bash
sudo yum install poppler-utils tesseract
```

## Installation

**Important:** The CLI depends on the core library, so install core first.

1. Install the core library:
```bash
cd core
pip install -e .
```

2. Navigate to the cli directory:
```bash
cd ../cli
```

3. Create and activate a virtual environment (recommended, if not already active):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install the CLI package:
```bash
pip install -e .
```

For development (includes pytest):
```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage
Compare two PDFs and output JSON to stdout:
```bash
pdf-ocr-diff document_v1.pdf document_v2.pdf
```

### Save Output to File
```bash
pdf-ocr-diff document_v1.pdf document_v2.pdf --output diff.json
```

### Adjust Image Resolution
Higher DPI provides better OCR accuracy but slower processing:
```bash
pdf-ocr-diff document_v1.pdf document_v2.pdf --dpi 200
```

### Help
```bash
pdf-ocr-diff --help
```

## Output Format

The tool outputs JSON with the following structure:

```json
{
  "pdf_a_path": "document_v1.pdf",
  "pdf_b_path": "document_v2.pdf",
  "total_pages_a": 5,
  "total_pages_b": 5,
  "total_differences": 12,
  "diff_items": [
    {
      "operation": "replace",
      "page_a": 1,
      "page_b": 1,
      "text_a": "Original text on page 1",
      "text_b": "Modified text on page 1",
      "bounding_boxes_a": [
        {
          "x": 100,
          "y": 200,
          "width": 300,
          "height": 50
        }
      ],
      "bounding_boxes_b": [
        {
          "x": 100,
          "y": 200,
          "width": 320,
          "height": 50
        }
      ]
    },
    {
      "operation": "insert",
      "page_a": 2,
      "page_b": 2,
      "text_a": null,
      "text_b": "New text added to page 2",
      "bounding_boxes_a": [],
      "bounding_boxes_b": [
        {
          "x": 150,
          "y": 400,
          "width": 250,
          "height": 40
        }
      ]
    }
  ]
}
```

### Field Descriptions

- **operation**: Type of difference - `equal`, `delete`, `insert`, or `replace`
- **page_a/page_b**: Page numbers in each PDF (null if page doesn't exist)
- **text_a/text_b**: Text content from each PDF (null if text doesn't exist)
- **bounding_boxes_a/bounding_boxes_b**: List of rectangular regions where text appears
  - **x, y**: Top-left corner coordinates (in pixels from PDF image)
  - **width, height**: Dimensions of the bounding box

## Running Tests

```bash
pytest
```

For verbose output:
```bash
pytest -v
```

## How It Works

1. **PDF to Images**: Converts each PDF page to an image at specified DPI (default 300)
2. **OCR Extraction**: Runs Tesseract OCR on each image to extract word-level text and bounding boxes
3. **Line Grouping**: Groups words into lines based on vertical proximity
4. **Page-by-Page Comparison**: Uses Python's difflib to compare text blocks between corresponding pages
5. **Spatial Mapping**: Maps each difference back to its bounding box coordinates on both pages
6. **JSON Output**: Serializes results to structured JSON format

## Known Limitations

- **OCR Accuracy**: Results depend on Tesseract OCR quality; poor scans or complex layouts may reduce accuracy
- **Layout Assumptions**: Words are grouped into lines based on vertical proximity with a fixed tolerance
- **Performance**: High DPI settings increase accuracy but slow processing, especially for large documents
- **Text-only**: Currently extracts and compares text only; does not detect image differences
- **Language**: Defaults to English OCR; other languages may require Tesseract language data

## Project Structure

```
cli/
├── pdf_ocr_diff/
│   ├── __init__.py
│   ├── models.py      # Data structures (BoundingBox, TextBlock, etc.)
│   ├── ocr.py         # PDF processing and OCR extraction
│   ├── differ.py      # Text comparison and spatial mapping
│   └── cli.py         # Command-line interface
├── tests/
│   ├── test_models.py
│   ├── test_ocr.py
│   └── test_differ.py
├── pyproject.toml
└── README.md
```

## License

MIT
