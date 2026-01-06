"""Command-line interface for PDF OCR diff tool."""

import argparse
import json
import sys
from pathlib import Path

from pdf_ocr_diff.ocr import process_pdf
from pdf_ocr_diff.differ import compare_pdfs


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Compare two PDFs using OCR and generate a spatial diff.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  pdf-ocr-diff doc_v1.pdf doc_v2.pdf
  pdf-ocr-diff doc_v1.pdf doc_v2.pdf --output diff.json
  pdf-ocr-diff doc_v1.pdf doc_v2.pdf --dpi 200
        '''
    )
    
    parser.add_argument('pdf_a', help='Path to the first PDF file')
    parser.add_argument('pdf_b', help='Path to the second PDF file')
    parser.add_argument('-o', '--output', 
                       help='Output file path for JSON results (default: stdout)',
                       default=None)
    parser.add_argument('--dpi', 
                       type=int, 
                       default=300,
                       help='DPI resolution for PDF to image conversion (default: 300)')
    parser.add_argument('--no-clean-stray-chars',
                       action='store_true',
                       help='Disable cleaning of stray trailing characters from OCR output')
    parser.add_argument('--line-height-tolerance',
                       type=int,
                       default=5,
                       help='Pixels of vertical tolerance for grouping words (deprecated, kept for compatibility)')
    
    args = parser.parse_args()
    
    # Validate input files
    pdf_a_path = Path(args.pdf_a)
    pdf_b_path = Path(args.pdf_b)
    
    if not pdf_a_path.exists():
        print(f"Error: First PDF file not found: {args.pdf_a}", file=sys.stderr)
        sys.exit(1)
    
    if not pdf_b_path.exists():
        print(f"Error: Second PDF file not found: {args.pdf_b}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Determine if stray character cleaning should be applied
        clean_stray_chars = not args.no_clean_stray_chars
        
        # Process first PDF
        print(f"Processing {args.pdf_a}...", file=sys.stderr)
        pages_a = process_pdf(str(pdf_a_path), dpi=args.dpi, clean_stray_chars=clean_stray_chars)
        print(f"  Extracted {len(pages_a)} pages", file=sys.stderr)
        
        # Process second PDF
        print(f"Processing {args.pdf_b}...", file=sys.stderr)
        pages_b = process_pdf(str(pdf_b_path), dpi=args.dpi, clean_stray_chars=clean_stray_chars)
        print(f"  Extracted {len(pages_b)} pages", file=sys.stderr)
        
        # Compare PDFs
        print("Computing differences...", file=sys.stderr)
        diff_result = compare_pdfs(pages_a, pages_b, args.pdf_a, args.pdf_b)
        print(f"  Found {len(diff_result.diff_items)} differences", file=sys.stderr)
        
        # Output results
        result_json = json.dumps(diff_result.to_dict(), indent=2)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(result_json)
            print(f"Results written to {args.output}", file=sys.stderr)
        else:
            print(result_json)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
