"""Diff computation module for comparing OCR results from two PDFs."""

import difflib
from difflib import SequenceMatcher
from typing import List, Optional

from .models import PageData, DiffItem, DiffOperation, DiffResult, BoundingBox, CharDiff


def _compute_char_diffs(text_a: str, text_b: str) -> List[CharDiff]:
    """
    Compute character-level differences between two strings.
    
    Args:
        text_a: Original text
        text_b: Modified text
    
    Returns:
        List of CharDiff objects showing character-level changes
    """
    matcher = SequenceMatcher(None, text_a, text_b)
    char_diffs = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        char_diff = CharDiff(
            operation=tag,
            text_a=text_a[i1:i2] if i1 < i2 else None,
            text_b=text_b[j1:j2] if j1 < j2 else None,
            start_a=i1,
            end_a=i2,
            start_b=j1,
            end_b=j2
        )
        char_diffs.append(char_diff)
    
    return char_diffs


def _generate_unified_diff(text_a: str, text_b: str, label_a: str = "a", label_b: str = "b") -> str:
    """
    Generate a unified diff string for character-level comparison.
    
    Args:
        text_a: Original text
        text_b: Modified text
        label_a: Label for the original text
        label_b: Label for the modified text
    
    Returns:
        Unified diff string
    """
    # Split into lines for unified_diff (though we're often comparing single lines)
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    
    # Add newline if not present to ensure proper diff formatting
    if lines_a and not lines_a[-1].endswith('\n'):
        lines_a[-1] += '\n'
    if lines_b and not lines_b[-1].endswith('\n'):
        lines_b[-1] += '\n'
    
    # Generate unified diff
    diff_lines = list(difflib.unified_diff(
        lines_a,
        lines_b,
        fromfile=label_a,
        tofile=label_b,
        lineterm=''
    ))
    
    return '\n'.join(diff_lines)


def _find_best_match(line: str, candidates: List[str], threshold: float = 0.6) -> Optional[int]:
    """
    Find the best matching line from candidates based on similarity.
    
    Args:
        line: Line to match
        candidates: List of candidate lines
        threshold: Minimum similarity ratio to consider a match
    
    Returns:
        Index of best match, or None if no good match found
    """
    best_ratio = 0.0
    best_idx = None
    
    for idx, candidate in enumerate(candidates):
        ratio = SequenceMatcher(None, line, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = idx
    
    return best_idx if best_ratio >= threshold else None


def _group_consecutive_diffs(diff_items: List[DiffItem], max_y_gap: int = 100, max_x_gap: int = 200) -> List[DiffItem]:
    """
    Group consecutive diff items of the same type that are spatially close.
    
    Args:
        diff_items: List of diff items to potentially group
        max_y_gap: Maximum vertical gap (pixels) to consider items as grouped
        max_x_gap: Maximum horizontal distance (pixels) between items' left edges
                   to consider them in the same column/section
    
    Returns:
        New list with consecutive items grouped where appropriate
    """
    if not diff_items:
        return []
    
    grouped = []
    current_group = [diff_items[0]]
    
    for item in diff_items[1:]:
        prev_item = current_group[-1]
        
        # Check if items can be grouped:
        # - Same operation type
        # - Same page numbers
        # - Vertically close (check last bbox of prev vs first bbox of current)
        # - Horizontally aligned (similar x position = same column/section)
        can_group = (item.operation == prev_item.operation and
                    item.page_a == prev_item.page_a and
                    item.page_b == prev_item.page_b)
        
        if can_group and prev_item.bounding_boxes_a and item.bounding_boxes_a:
            prev_bbox = prev_item.bounding_boxes_a[-1]
            curr_bbox = item.bounding_boxes_a[0]
            
            # Check vertical distance
            if abs(curr_bbox.y - prev_bbox.y) > max_y_gap:
                can_group = False
            # Check horizontal alignment (are they in the same column?)
            elif abs(curr_bbox.x - prev_bbox.x) > max_x_gap:
                can_group = False
                
        elif can_group and prev_item.bounding_boxes_b and item.bounding_boxes_b:
            prev_bbox = prev_item.bounding_boxes_b[-1]
            curr_bbox = item.bounding_boxes_b[0]
            
            # Check vertical distance
            if abs(curr_bbox.y - prev_bbox.y) > max_y_gap:
                can_group = False
            # Check horizontal alignment (are they in the same column?)
            elif abs(curr_bbox.x - prev_bbox.x) > max_x_gap:
                can_group = False
        
        if can_group:
            current_group.append(item)
        else:
            # Flush current group
            if len(current_group) > 1:
                # Merge group into single item
                grouped.append(_merge_diff_items(current_group))
            else:
                grouped.append(current_group[0])
            current_group = [item]
    
    # Flush last group
    if len(current_group) > 1:
        grouped.append(_merge_diff_items(current_group))
    else:
        grouped.append(current_group[0])
    
    return grouped


def _merge_diff_items(items: List[DiffItem]) -> DiffItem:
    """
    Merge multiple diff items into a single item.
    
    Args:
        items: List of diff items to merge (must all have same operation)
    
    Returns:
        Single merged DiffItem
    """
    texts_a = [item.text_a for item in items if item.text_a]
    texts_b = [item.text_b for item in items if item.text_b]
    bboxes_a = [bbox for item in items for bbox in item.bounding_boxes_a]
    bboxes_b = [bbox for item in items for bbox in item.bounding_boxes_b]
    
    # Use newlines to preserve line structure instead of spaces
    merged_text_a = '\n'.join(texts_a) if texts_a else None
    merged_text_b = '\n'.join(texts_b) if texts_b else None
    
    # Generate unified diff and char diffs for merged text if it's a replace
    unified_diff = None
    char_diffs = []
    if merged_text_a and merged_text_b:
        unified_diff = _generate_unified_diff(
            merged_text_a, merged_text_b,
            f"page_{items[0].page_a}",
            f"page_{items[0].page_b}"
        )
        char_diffs = _compute_char_diffs(merged_text_a, merged_text_b)
    
    return DiffItem(
        operation=items[0].operation,
        page_a=items[0].page_a,
        page_b=items[0].page_b,
        text_a=merged_text_a,
        text_b=merged_text_b,
        bounding_boxes_a=bboxes_a,
        bounding_boxes_b=bboxes_b,
        unified_diff=unified_diff,
        char_diffs=char_diffs
    )


def compare_pages(page_a: Optional[PageData], page_b: Optional[PageData]) -> List[DiffItem]:
    """
    Compare two pages and generate diff items.
    
    Args:
        page_a: PageData from first PDF (can be None if page doesn't exist)
        page_b: PageData from second PDF (can be None if page doesn't exist)
    
    Returns:
        List of DiffItem objects representing differences
    """
    diff_items = []
    
    # Handle missing pages
    if page_a is None and page_b is None:
        return diff_items
    
    if page_a is None:
        # Page only exists in B (insert)
        for block in page_b.text_blocks:
            diff_items.append(DiffItem(
                operation=DiffOperation.INSERT,
                page_a=None,
                page_b=page_b.page_number,
                text_a=None,
                text_b=block.text,
                bounding_boxes_a=[],
                bounding_boxes_b=[block.bounding_box]
            ))
        return diff_items
    
    if page_b is None:
        # Page only exists in A (delete)
        for block in page_a.text_blocks:
            diff_items.append(DiffItem(
                operation=DiffOperation.DELETE,
                page_a=page_a.page_number,
                page_b=None,
                text_a=block.text,
                text_b=None,
                bounding_boxes_a=[block.bounding_box],
                bounding_boxes_b=[]
            ))
        return diff_items
    
    # Both pages exist - compare line by line
    lines_a = [block.text for block in page_a.text_blocks]
    lines_b = [block.text for block in page_b.text_blocks]
    
    # Use autojunk=False for more accurate matching
    matcher = SequenceMatcher(None, lines_a, lines_b, autojunk=False)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Lines are the same - skip (we only track differences)
            continue
        elif tag == 'delete':
            # Lines only in A - create one diff item per line
            for i in range(i1, i2):
                diff_items.append(DiffItem(
                    operation=DiffOperation.DELETE,
                    page_a=page_a.page_number,
                    page_b=page_b.page_number,
                    text_a=lines_a[i],
                    text_b=None,
                    bounding_boxes_a=[page_a.text_blocks[i].bounding_box],
                    bounding_boxes_b=[]
                ))
        elif tag == 'insert':
            # Lines only in B - create one diff item per line
            for j in range(j1, j2):
                diff_items.append(DiffItem(
                    operation=DiffOperation.INSERT,
                    page_a=page_a.page_number,
                    page_b=page_b.page_number,
                    text_a=None,
                    text_b=lines_b[j],
                    bounding_boxes_a=[],
                    bounding_boxes_b=[page_b.text_blocks[j].bounding_box]
                ))
        elif tag == 'replace':
            # Lines differ between A and B
            # For equal-length replacements, pair them up line-by-line
            # For unequal lengths, treat extras as insert/delete
            num_a = i2 - i1
            num_b = j2 - j1
            min_lines = min(num_a, num_b)
            
            # Create replace items for paired lines
            for idx in range(min_lines):
                i = i1 + idx
                j = j1 + idx
                
                # Generate unified diff for this line pair
                unified_diff = _generate_unified_diff(
                    lines_a[i],
                    lines_b[j],
                    f"page_{page_a.page_number}_line_{i}",
                    f"page_{page_b.page_number}_line_{j}"
                )
                
                # Compute character-level diffs
                char_diffs = _compute_char_diffs(lines_a[i], lines_b[j])
                
                diff_items.append(DiffItem(
                    operation=DiffOperation.REPLACE,
                    page_a=page_a.page_number,
                    page_b=page_b.page_number,
                    text_a=lines_a[i],
                    text_b=lines_b[j],
                    bounding_boxes_a=[page_a.text_blocks[i].bounding_box],
                    bounding_boxes_b=[page_b.text_blocks[j].bounding_box],
                    unified_diff=unified_diff,
                    char_diffs=char_diffs
                ))
            
            # Handle extra lines in A (deletions)
            for i in range(i1 + min_lines, i2):
                diff_items.append(DiffItem(
                    operation=DiffOperation.DELETE,
                    page_a=page_a.page_number,
                    page_b=page_b.page_number,
                    text_a=lines_a[i],
                    text_b=None,
                    bounding_boxes_a=[page_a.text_blocks[i].bounding_box],
                    bounding_boxes_b=[]
                ))
            
            # Handle extra lines in B (insertions)
            for j in range(j1 + min_lines, j2):
                diff_items.append(DiffItem(
                    operation=DiffOperation.INSERT,
                    page_a=page_a.page_number,
                    page_b=page_b.page_number,
                    text_a=None,
                    text_b=lines_b[j],
                    bounding_boxes_a=[],
                    bounding_boxes_b=[page_b.text_blocks[j].bounding_box]
                ))
    
    # Group consecutive diffs that are spatially close
    diff_items = _group_consecutive_diffs(diff_items)
    
    return diff_items


def compare_pdfs(pages_a: List[PageData], pages_b: List[PageData], 
                 pdf_a_path: str, pdf_b_path: str) -> DiffResult:
    """
    Compare two PDFs page by page and generate a complete diff result.
    
    Args:
        pages_a: List of PageData from first PDF
        pages_b: List of PageData from second PDF
        pdf_a_path: Path to first PDF
        pdf_b_path: Path to second PDF
    
    Returns:
        DiffResult containing all differences
    """
    all_diff_items = []
    
    # Compare pages up to the length of the shorter PDF
    max_pages = max(len(pages_a), len(pages_b))
    
    for page_num in range(max_pages):
        page_a = pages_a[page_num] if page_num < len(pages_a) else None
        page_b = pages_b[page_num] if page_num < len(pages_b) else None
        
        page_diffs = compare_pages(page_a, page_b)
        all_diff_items.extend(page_diffs)
    
    return DiffResult(
        pdf_a_path=pdf_a_path,
        pdf_b_path=pdf_b_path,
        total_pages_a=len(pages_a),
        total_pages_b=len(pages_b),
        diff_items=all_diff_items
    )
