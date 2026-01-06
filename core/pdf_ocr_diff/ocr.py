"""OCR processing module for extracting text with spatial data from PDFs."""

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import List
import pandas as pd
import re

from .models import PageData, TextBlock, BoundingBox


def group_words_into_lines(ocr_data: pd.DataFrame, line_height_tolerance: int = 5) -> List[TextBlock]:
    """
    Group word-level OCR results into lines using Tesseract's native line detection.
    
    Uses Tesseract's block_num and line_num fields to group words when available,
    which respects the reading order detected by Tesseract. This fixes word order
    issues like "8 people Serves" -> "Serves 8 people".
    
    Falls back to coordinate-based grouping if Tesseract metadata is not available.
    
    Args:
        ocr_data: DataFrame from pytesseract.image_to_data
        line_height_tolerance: Pixels of vertical tolerance for fallback coordinate-based grouping
    
    Returns:
        List of TextBlock objects representing lines of text
    """
    # Handle empty DataFrame
    if ocr_data.empty:
        return []
    
    # Filter out empty text and confidence -1 (non-text blocks)
    valid_data = ocr_data[(ocr_data['conf'] != -1) & (ocr_data['text'].astype(str).str.strip() != '')]
    
    if valid_data.empty:
        return []
    
    # Check if Tesseract metadata columns are available
    has_tesseract_metadata = all(col in valid_data.columns for col in ['block_num', 'par_num', 'line_num', 'word_num'])
    
    if has_tesseract_metadata:
        # Use Tesseract's native line detection (preferred method)
        return _group_by_tesseract_lines(valid_data)
    else:
        # Fall back to coordinate-based grouping
        return _group_by_coordinates(valid_data, line_height_tolerance)


def _group_by_tesseract_lines(valid_data: pd.DataFrame, horizontal_gap_threshold: int = 100) -> List[TextBlock]:
    """
    Group words using Tesseract's native block/line metadata with horizontal gap detection.
    
    This method respects Tesseract's reading order while also splitting lines when
    words are too far apart horizontally (e.g., in multi-column layouts).
    
    Args:
        valid_data: Filtered DataFrame with OCR data
        horizontal_gap_threshold: Maximum horizontal gap in pixels between words
                                 in the same semantic line (default: 100)
    """
    # Sort by block, paragraph, line, then word number to get proper order
    valid_data = valid_data.sort_values(['block_num', 'par_num', 'line_num', 'word_num'])
    
    lines = []
    line_number = 0
    
    # Group words by (block_num, par_num, line_num)
    grouped = valid_data.groupby(['block_num', 'par_num', 'line_num'])
    
    for group_key, group_data in grouped:
        current_line_words = []
        
        for _, row in group_data.iterrows():
            word_text = str(row['text']).strip()
            word_top = row['top']
            word_left = row['left']
            word_width = row['width']
            word_height = row['height']
            
            word_dict = {
                'text': word_text,
                'left': word_left,
                'top': word_top,
                'width': word_width,
                'height': word_height
            }
            
            # Check if this word is too far from the previous word horizontally
            if current_line_words:
                last_word = current_line_words[-1]
                last_word_right = last_word['left'] + last_word['width']
                horizontal_gap = word_left - last_word_right
                
                # If gap is too large, flush current line and start a new one
                if horizontal_gap > horizontal_gap_threshold:
                    lines.append(_create_text_block_from_words(current_line_words, line_number))
                    line_number += 1
                    current_line_words = [word_dict]
                else:
                    current_line_words.append(word_dict)
            else:
                current_line_words.append(word_dict)
        
        # Flush any remaining words in this Tesseract line
        if current_line_words:
            lines.append(_create_text_block_from_words(current_line_words, line_number))
            line_number += 1
    
    return lines


def _group_by_coordinates(valid_data: pd.DataFrame, line_height_tolerance: int) -> List[TextBlock]:
    """
    Group words by vertical proximity (legacy/fallback method).
    
    This method is less accurate than using Tesseract metadata but works
    when metadata is unavailable (e.g., in tests or with other OCR engines).
    """
    # Sort by top coordinate, then left coordinate
    valid_data = valid_data.sort_values(['top', 'left'])
    
    lines = []
    current_line_words = []
    current_line_top = None
    line_number = 0
    
    for _, row in valid_data.iterrows():
        word_text = str(row['text']).strip()
        word_top = row['top']
        word_left = row['left']
        word_width = row['width']
        word_height = row['height']
        
        # Check if this word belongs to the current line
        if current_line_top is None or abs(word_top - current_line_top) <= line_height_tolerance:
            # Same line or first word
            current_line_words.append({
                'text': word_text,
                'left': word_left,
                'top': word_top,
                'width': word_width,
                'height': word_height
            })
            if current_line_top is None:
                current_line_top = word_top
        else:
            # New line - flush current line
            if current_line_words:
                lines.append(_create_text_block_from_words(current_line_words, line_number))
                line_number += 1
            
            # Start new line
            current_line_words = [{
                'text': word_text,
                'left': word_left,
                'top': word_top,
                'width': word_width,
                'height': word_height
            }]
            current_line_top = word_top
    
    # Flush the last line
    if current_line_words:
        lines.append(_create_text_block_from_words(current_line_words, line_number))
    
    return lines


def _clean_stray_characters(text_blocks: List[TextBlock]) -> List[TextBlock]:
    """
    Remove trailing single characters and standalone single-character blocks that are likely OCR errors.
    
    Detects patterns like:
    - "Vanilla e" where a stray character is incorrectly appended
    - Standalone "e" or "S" blocks that are OCR artifacts
    
    Args:
        text_blocks: List of TextBlock objects
    
    Returns:
        List of TextBlock objects with cleaned text (empty blocks removed)
    """
    cleaned_blocks = []
    
    for block in text_blocks:
        text = block.text.strip()
        
        # Skip standalone single characters (likely stray OCR artifacts)
        if len(text) == 1 and text.isalpha():
            continue  # Skip this block entirely
        
        # Pattern: ends with space + single alphabetic character
        # Examples: "Vanilla e", "Recipe s", "Title i"
        if re.match(r'^.+ [a-zA-Z]$', text):
            # Strip the last 2 characters (space + letter)
            cleaned_text = text[:-2]
            # Create new TextBlock with cleaned text, preserving bounding box
            cleaned_block = TextBlock(
                text=cleaned_text,
                bounding_box=block.bounding_box,
                line_number=block.line_number
            )
            cleaned_blocks.append(cleaned_block)
        else:
            # No cleaning needed
            cleaned_blocks.append(block)
    
    return cleaned_blocks


def _sort_blocks_spatially(text_blocks: List[TextBlock], 
                           column_threshold: int = 400,
                           min_column_blocks: int = 3,
                           row_tolerance: int = 50) -> List[TextBlock]:
    """
    Sort text blocks by spatial position with intelligent column/row detection.
    
    Detects true multi-column layouts (with multiple blocks per column) and sorts
    those by column. For single-column or mixed layouts, sorts primarily by row
    (top-to-bottom), with left-to-right ordering within each row.
    
    Args:
        text_blocks: List of TextBlock objects to sort
        column_threshold: Horizontal distance to consider blocks in different columns
        min_column_blocks: Minimum blocks needed to consider a column valid
        row_tolerance: Vertical distance to consider blocks on the same row
    
    Returns:
        Sorted list of TextBlock objects
    """
    if not text_blocks:
        return []
    
    # Detect potential columns by clustering x positions
    x_positions = sorted([b.bounding_box.x for b in text_blocks])
    
    # Group x positions into potential columns
    potential_columns = []
    if x_positions:
        current_column_x = [x_positions[0]]
        for x in x_positions[1:]:
            if x - current_column_x[-1] < column_threshold:
                current_column_x.append(x)
            else:
                # New potential column
                potential_columns.append(current_column_x)
                current_column_x = [x]
        if current_column_x:
            potential_columns.append(current_column_x)
    
    # Filter to only "real" columns (those with enough blocks)
    real_columns = [col for col in potential_columns if len(col) >= min_column_blocks]
    
    # Decide sorting strategy based on column detection
    if len(real_columns) >= 2:
        # Multi-column layout detected - use column-based sorting
        return _sort_by_columns(text_blocks, real_columns, column_threshold)
    else:
        # Single column or mixed layout - use row-based sorting
        return _sort_by_rows(text_blocks, row_tolerance)


def _sort_by_columns(text_blocks: List[TextBlock], column_x_groups: List[List[int]], 
                     column_threshold: int) -> List[TextBlock]:
    """
    Sort blocks by columns (for true multi-column layouts).
    
    Args:
        text_blocks: List of TextBlock objects
        column_x_groups: List of x-position groups for each column
        column_threshold: Distance threshold for column assignment
    
    Returns:
        Sorted blocks (left column top-to-bottom, then right column, etc.)
    """
    # Calculate average x for each column
    columns_x = [sum(col) / len(col) for col in column_x_groups]
    
    # Assign each block to nearest column
    def get_column_index(block: TextBlock) -> int:
        block_x = block.bounding_box.x
        min_dist = float('inf')
        col_idx = 0
        for idx, col_x in enumerate(columns_x):
            dist = abs(block_x - col_x)
            if dist < min_dist:
                min_dist = dist
                col_idx = idx
        return col_idx
    
    # Group blocks by column
    column_blocks = {i: [] for i in range(len(columns_x))}
    for block in text_blocks:
        col_idx = get_column_index(block)
        column_blocks[col_idx].append(block)
    
    # Sort each column by y position (top to bottom)
    for col_idx in column_blocks:
        column_blocks[col_idx].sort(key=lambda b: b.bounding_box.y)
    
    # Concatenate columns left to right
    result = []
    for col_idx in sorted(column_blocks.keys()):
        result.extend(column_blocks[col_idx])
    
    return result


def _sort_by_rows(text_blocks: List[TextBlock], row_tolerance: int) -> List[TextBlock]:
    """
    Sort blocks by rows (for single-column or mixed layouts).
    
    Groups blocks into rows based on vertical proximity, then sorts each row
    left-to-right. This handles centered text, varied indentation, etc.
    
    Args:
        text_blocks: List of TextBlock objects
        row_tolerance: Vertical distance to consider blocks on the same row
    
    Returns:
        Sorted blocks (top-to-bottom, left-to-right within rows)
    """
    if not text_blocks:
        return []
    
    # Sort by y first to find rows
    sorted_by_y = sorted(text_blocks, key=lambda b: b.bounding_box.y)
    
    # Group into rows based on vertical proximity
    rows = []
    current_row = [sorted_by_y[0]]
    
    for block in sorted_by_y[1:]:
        # Check if this block is close enough to be in the current row
        row_y_avg = sum(b.bounding_box.y for b in current_row) / len(current_row)
        if abs(block.bounding_box.y - row_y_avg) <= row_tolerance:
            current_row.append(block)
        else:
            # Start new row
            current_row.sort(key=lambda b: b.bounding_box.x)  # Sort row left-to-right
            rows.append(current_row)
            current_row = [block]
    
    # Add last row
    if current_row:
        current_row.sort(key=lambda b: b.bounding_box.x)
        rows.append(current_row)
    
    # Flatten rows into single list
    result = []
    for row in rows:
        result.extend(row)
    
    return result


def _create_text_block_from_words(words: List[dict], line_number: int) -> TextBlock:
    """
    Create a TextBlock from a list of words on the same line.
    
    Args:
        words: List of word dictionaries with text and coordinates
        line_number: The line number for this text block
    
    Returns:
        TextBlock with combined text and bounding box
    """
    # Combine text with spaces
    combined_text = ' '.join(word['text'] for word in words)
    
    # Calculate bounding box that encompasses all words
    min_left = min(word['left'] for word in words)
    max_right = max(word['left'] + word['width'] for word in words)
    min_top = min(word['top'] for word in words)
    max_bottom = max(word['top'] + word['height'] for word in words)
    
    bbox = BoundingBox(
        x=min_left,
        y=min_top,
        width=max_right - min_left,
        height=max_bottom - min_top
    )
    
    return TextBlock(text=combined_text, bounding_box=bbox, line_number=line_number)


def process_page_with_ocr(image: Image.Image, page_number: int, clean_stray_chars: bool = True) -> PageData:
    """
    Process a single page image with OCR and extract text with spatial data.
    
    Args:
        image: PIL Image object of the page
        page_number: Page number (1-indexed)
        clean_stray_chars: Whether to apply stray character cleaning (default: True)
    
    Returns:
        PageData object containing OCR results
    """
    # Get OCR data with word-level bounding boxes
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
    
    # Group words into lines
    text_blocks = group_words_into_lines(ocr_data)
    
    # Clean stray characters if enabled
    if clean_stray_chars:
        text_blocks = _clean_stray_characters(text_blocks)
    
    # Sort blocks by spatial position (top-to-bottom, left-to-right within same row)
    # This ensures proper reading order after horizontal gap splitting
    text_blocks = _sort_blocks_spatially(text_blocks)
    
    # Reassign line numbers after sorting
    for i, block in enumerate(text_blocks):
        block.line_number = i
    
    return PageData(
        page_number=page_number,
        text_blocks=text_blocks,
        image_width=image.width,
        image_height=image.height
    )


def process_pdf(pdf_path: str, dpi: int = 300, clean_stray_chars: bool = True) -> List[PageData]:
    """
    Process a PDF file and extract OCR data for all pages.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for converting PDF pages to images
        clean_stray_chars: Whether to apply stray character cleaning (default: True)
    
    Returns:
        List of PageData objects, one per page
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)
    
    # Process each page
    pages_data = []
    for page_num, image in enumerate(images, start=1):
        page_data = process_page_with_ocr(image, page_num, clean_stray_chars=clean_stray_chars)
        pages_data.append(page_data)
    
    return pages_data
