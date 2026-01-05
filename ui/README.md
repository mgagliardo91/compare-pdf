# PDF OCR Diff UI - Phase 2

React-based UI for viewing side-by-side PDF comparisons with visual diff overlays.

## Implementation Status

### ✅ Completed (Phase 2.1 - Basic Prototype)

- [x] Project scaffolding (Vite + React + TypeScript)
- [x] Dependencies installed (MUI, react-pdf, zustand)
- [x] TypeScript type definitions (`types/diff.ts`)
- [x] Zustand store for state management (`store/diffStore.ts`)
- [x] Basic App component with asset loading
- [x] Side-by-side PDF viewer with react-pdf
- [x] Bounding box overlay rendering
- [x] Basic hover highlighting
- [x] Simple diff popover display
- [x] Environment configuration
- [x] Asset setup scripts

### 🚧 TODO (Future Enhancements)

- [ ] Advanced scroll synchronization (currently basic)
- [ ] Character-level diff visualization in popover
- [ ] Zoom controls
- [ ] Navigation between diffs (prev/next buttons)
- [ ] Responsive layout for smaller screens
- [ ] Performance optimization for large PDFs
- [ ] Better error boundaries
- [ ] Loading skeleton components

## Quick Start

### 1. Install Dependencies

```bash
cd ui
npm install
```

### 2. Copy Example Assets

```bash
# Copy example PDFs and diff output to public directory
cp ../example/first.pdf public/pdfs/
cp ../example/second.pdf public/pdfs/
cp ../example/diff_output.json public/diffs/
```

### 3. Configure Environment

Create `.env` in the `ui/` directory:

```env
VITE_PDF_A_PATH=/pdfs/first.pdf
VITE_PDF_B_PATH=/pdfs/second.pdf
VITE_DIFF_JSON_PATH=/diffs/diff_output.json
```

### 4. Run Development Server

```bash
npm run dev
```

Visit http://localhost:5173

## Project Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── App.tsx              # Main app with asset loading
│   │   ├── PDFCompareView.tsx   # Side-by-side layout
│   │   ├── PDFPane.tsx          # Single PDF viewer
│   │   ├── DiffOverlay.tsx      # Bounding box renderer
│   │   └── DiffPopover.tsx      # Hover tooltip
│   ├── store/
│   │   └── diffStore.ts         # Zustand state management
│   ├── types/
│   │   └── diff.ts              # TypeScript interfaces
│   └── main.tsx                 # Entry point
├── public/
│   ├── pdfs/                    # Place PDF files here
│   └── diffs/                   # Place diff JSON here
└── .env                         # Environment configuration
```

## Features Implemented

### 1. Side-by-Side PDF Viewing
- Both PDFs rendered using react-pdf
- Vertical scrolling for multi-page documents
- Basic scroll sync between panes

### 2. Diff Overlays
- Bounding boxes drawn over PDF pages
- Color-coded by operation type:
  - Replace: Orange border
  - Insert: Green border
  - Delete: Red border

### 3. Interactive Highlighting
- Hover over a diff box to highlight it
- Cross-highlighting: hovering one side highlights the corresponding region on the other
- Z-index elevation for active highlights

### 4. Diff Details Popover
- Shows text from both sides
- Displays operation type
- Positioned near the hovered box

## Technical Details

### Coordinate Transformation

OCR bounding boxes are in raster coordinates (300 DPI by default). The UI transforms these to match the rendered PDF scale:

```typescript
const scaleFactor = renderedWidth / ocrRasterWidth;
const displayX = ocrX * scaleFactor;
const displayY = ocrY * scaleFactor;
```

**Assumptions:**
- Origin (0,0) is at top-left corner
- OCR used 300 DPI (2550px width for standard 8.5" page)
- Bounding boxes are in pixel coordinates

### State Management

Uses Zustand for lightweight global state:
- `diffData`: Loaded diff JSON
- `activeDiffIndex`: Currently hovered diff item
- `isLoading`: Loading state
- `error`: Error messages

## Known Limitations (v0.1)

1. **Scroll sync is approximate** - Works but may drift slightly
2. **No zoom controls** - PDFs render at fixed width
3. **Character-level diffs not visualized** - Shows full text only
4. **No diff navigation** - Must hover each diff manually
5. **Simple error handling** - Basic error messages only

## Testing with Different PDFs

To test with your own PDFs:

1. Generate diff using Phase 1 CLI:
```bash
cd ..
.venv/bin/pdf-ocr-diff your_pdf_a.pdf your_pdf_b.pdf -o ui/public/diffs/your_diff.json
```

2. Copy PDFs to public:
```bash
cp your_pdf_a.pdf ui/public/pdfs/
cp your_pdf_b.pdf ui/public/pdfs/
```

3. Update `.env`:
```env
VITE_PDF_A_PATH=/pdfs/your_pdf_a.pdf
VITE_PDF_B_PATH=/pdfs/your_pdf_b.pdf
VITE_DIFF_JSON_PATH=/diffs/your_diff.json
```

## Troubleshooting

### PDFs Not Loading
- Check that file paths in `.env` match files in `public/`
- Verify PDFs aren't corrupted: `pdfinfo public/pdfs/first.pdf`
- Check browser console for CORS errors

### Bounding Boxes Misaligned
- Ensure Phase 1 OCR used 300 DPI: `--dpi 300` (default)
- Check scale factor in DevTools: `renderedWidth / 2550`
- Verify PDF dimensions match between OCR and rendering

### Diff JSON Not Loading
- Validate JSON: `jq . public/diffs/diff_output.json`
- Check file permissions: `ls -la public/diffs/`
- Ensure path starts with `/` in `.env`

## Development Notes

### Adding New Components

Place in `src/components/` and import into `App.tsx`.

### Modifying Diff Display

Edit `DiffPopover.tsx` to change how diffs are shown.

### Adjusting Colors

Update color constants in component files:
- Replace: `#ff9800` (orange)
- Insert: `#4caf50` (green)  
- Delete: `#f44336` (red)

## Building for Production

```bash
npm run build
```

Output in `dist/` can be served with any static server:
```bash
npx serve dist
```

## Next Steps for Future Development

1. **Scroll Sync Enhancement**: Implement proper scroll ratio calculation with debouncing
2. **Char Diff Visualization**: Parse `char_diffs` and highlight inline
3. **Diff Navigation**: Add prev/next buttons and keyboard shortcuts
4. **Zoom Controls**: Allow PDF scaling
5. **Mobile Support**: Responsive layout with stacked PDFs
6. **Performance**: Virtualize page rendering for large PDFs
7. **Accessibility**: ARIA labels, keyboard navigation

## Session Continuity

When returning to this project in a new session:

1. Check implementation status above
2. Review `src/components/` to see completed components
3. Run `npm run dev` to verify current state
4. Pick next TODO item from the list
5. Test with `example/` PDFs first

## Phase 1 CLI Integration

The UI consumes JSON from the Phase 1 CLI tool located in the parent directory:

```bash
cd ..
.venv/bin/pdf-ocr-diff --help
```

Generate new diffs for testing UI updates.
