# Quick Start Guide

## Running the UI Prototype (Fastest Way to See Results)

```bash
cd ui
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

You should see:
- Two PDFs side-by-side (first.pdf and second.pdf)
- Orange/red/green boxes highlighting differences
- Hover over any box to see what changed

## Running the CLI Tool

```bash
# From project root
.venv/bin/pdf-ocr-diff example/first.pdf example/second.pdf

# Save to file
.venv/bin/pdf-ocr-diff example/first.pdf example/second.pdf -o my_diff.json

# Use custom DPI
.venv/bin/pdf-ocr-diff --dpi 200 doc1.pdf doc2.pdf
```

## Testing with Your Own PDFs

### 1. Generate a Diff
```bash
.venv/bin/pdf-ocr-diff your_doc_v1.pdf your_doc_v2.pdf -o ui/public/diffs/my_diff.json
```

### 2. Copy PDFs to UI
```bash
cp your_doc_v1.pdf ui/public/pdfs/
cp your_doc_v2.pdf ui/public/pdfs/
```

### 3. Update UI Config
Edit `ui/.env`:
```env
VITE_PDF_A_PATH=/pdfs/your_doc_v1.pdf
VITE_PDF_B_PATH=/pdfs/your_doc_v2.pdf
VITE_DIFF_JSON_PATH=/diffs/my_diff.json
```

### 4. Reload UI
```bash
cd ui
npm run dev
```

## Project Organization

- **Phase 1 (CLI)**: `pdf_ocr_diff/` - Python tool for generating diffs
- **Phase 2 (UI)**: `ui/` - React app for visualizing diffs
- **Examples**: `example/` - Sample PDFs and diff outputs
- **Tests**: `tests/` - Unit tests for CLI
- **Docs**: `README.md`, `IMPLEMENTATION_STATUS.md`

## Common Issues

**"PDFs not loading in UI"**
→ Check that `.env` paths match files in `public/`

**"Bounding boxes misaligned"**
→ Ensure OCR used 300 DPI (the default)

**"No differences shown"**
→ Check diff JSON has `diff_items` array with content

**"Import errors in UI"**
→ Run `npm install` in `ui/` directory

## Next Steps

1. ✅ Try the example PDFs
2. ✅ Test with your own documents
3. 📖 Read `IMPLEMENTATION_STATUS.md` for details
4. 🚀 Check `ui/README.md` for UI enhancements to add
