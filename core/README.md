# PDF OCR Diff Core

Core library containing the PDF OCR diff logic. This package is used by both the CLI and API.

## Features

- **OCR Extraction**: Extract text and bounding boxes from PDF pages using Tesseract
- **Diff Computation**: Compare PDFs page-by-page with spatial awareness
- **Data Models**: Structured models for diffs, bounding boxes, and page data

## Installation

```bash
cd core
pip install -e .
```

## Usage

This is a library package meant to be imported by other components:

```python
from pdf_ocr_diff.ocr import process_pdf
from pdf_ocr_diff.differ import compare_documents
from pdf_ocr_diff.models import DiffResult

# Process PDFs
pages_a = process_pdf("document1.pdf", dpi=300)
pages_b = process_pdf("document2.pdf", dpi=300)

# Compare
result = compare_documents(
    pages_a=pages_a,
    pages_b=pages_b,
    pdf_a_path="document1.pdf",
    pdf_b_path="document2.pdf"
)

# Access results
print(f"Total differences: {len(result.diff_items)}")
for diff in result.diff_items:
    print(f"{diff.operation}: {diff.text_a} -> {diff.text_b}")

# Convert to JSON
json_output = result.to_dict()
```

## Modules

- `models.py` - Data structures (BoundingBox, TextBlock, DiffItem, DiffResult)
- `ocr.py` - PDF to image conversion and OCR extraction
- `differ.py` - Text comparison and spatial diff computation

## Dependencies

- pdf2image - PDF to image conversion
- pytesseract - OCR text extraction
- Pillow - Image processing
- pandas - Data manipulation

## System Requirements

Requires system-level dependencies:
- poppler (for PDF rendering)
- tesseract (for OCR)

## Testing

The core library includes a comprehensive test suite:

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_differ.py
```

Test coverage includes:
- **test_models.py** - Data structure serialization
- **test_ocr.py** - Text extraction and line grouping
- **test_differ.py** - Diff computation and spatial mapping

## License

MIT
