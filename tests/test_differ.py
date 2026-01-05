"""Tests for differ module."""

from pdf_ocr_diff.models import (
    BoundingBox, TextBlock, PageData, DiffOperation
)
from pdf_ocr_diff.differ import (
    compare_pages, compare_pdfs, _compute_char_diffs, _infer_operation_from_char_diffs
)


def test_compare_pages_identical():
    """Test comparing two identical pages."""
    bbox1 = BoundingBox(x=10, y=20, width=100, height=50)
    block1 = TextBlock(text="Same text", bounding_box=bbox1, line_number=0)
    
    page_a = PageData(page_number=1, text_blocks=[block1])
    page_b = PageData(page_number=1, text_blocks=[block1])
    
    result = compare_pages(page_a, page_b)
    
    # Identical pages should have no differences
    assert len(result) == 0


def test_compare_pages_different():
    """Test comparing two different pages."""
    bbox1 = BoundingBox(x=10, y=20, width=100, height=50)
    bbox2 = BoundingBox(x=10, y=20, width=100, height=50)
    
    block_a = TextBlock(text="Text A", bounding_box=bbox1, line_number=0)
    block_b = TextBlock(text="Text B", bounding_box=bbox2, line_number=0)
    
    page_a = PageData(page_number=1, text_blocks=[block_a])
    page_b = PageData(page_number=1, text_blocks=[block_b])
    
    result = compare_pages(page_a, page_b)
    
    assert len(result) == 1
    assert result[0].operation == DiffOperation.REPLACE
    assert result[0].text_a == "Text A"
    assert result[0].text_b == "Text B"
    assert len(result[0].bounding_boxes_a) == 1
    assert len(result[0].bounding_boxes_b) == 1


def test_compare_pages_missing_page_a():
    """Test comparing when page A is missing."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block = TextBlock(text="New page", bounding_box=bbox, line_number=0)
    page_b = PageData(page_number=2, text_blocks=[block])
    
    result = compare_pages(None, page_b)
    
    assert len(result) == 1
    assert result[0].operation == DiffOperation.INSERT
    assert result[0].text_a is None
    assert result[0].text_b == "New page"
    assert result[0].page_a is None
    assert result[0].page_b == 2


def test_compare_pages_missing_page_b():
    """Test comparing when page B is missing."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block = TextBlock(text="Deleted page", bounding_box=bbox, line_number=0)
    page_a = PageData(page_number=3, text_blocks=[block])
    
    result = compare_pages(page_a, None)
    
    assert len(result) == 1
    assert result[0].operation == DiffOperation.DELETE
    assert result[0].text_a == "Deleted page"
    assert result[0].text_b is None
    assert result[0].page_a == 3
    assert result[0].page_b is None


def test_compare_pages_insert_delete():
    """Test comparing pages with insertions and deletions."""
    bbox1 = BoundingBox(x=10, y=20, width=100, height=50)
    bbox2 = BoundingBox(x=10, y=80, width=100, height=50)
    bbox3 = BoundingBox(x=10, y=140, width=100, height=50)
    
    block_a1 = TextBlock(text="Line 1", bounding_box=bbox1, line_number=0)
    block_a2 = TextBlock(text="Line 2", bounding_box=bbox2, line_number=1)
    
    block_b1 = TextBlock(text="Line 1", bounding_box=bbox1, line_number=0)
    block_b2 = TextBlock(text="New line", bounding_box=bbox3, line_number=1)
    block_b3 = TextBlock(text="Line 2", bounding_box=bbox2, line_number=2)
    
    page_a = PageData(page_number=1, text_blocks=[block_a1, block_a2])
    page_b = PageData(page_number=1, text_blocks=[block_b1, block_b2, block_b3])
    
    result = compare_pages(page_a, page_b)
    
    # Should detect the insertion (one diff item for the inserted line)
    assert len(result) == 1
    assert result[0].operation == DiffOperation.INSERT
    assert result[0].text_b == "New line"


def test_compare_pdfs():
    """Test comparing two complete PDFs."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block_a = TextBlock(text="Page 1 A", bounding_box=bbox, line_number=0)
    block_b = TextBlock(text="Page 1 B", bounding_box=bbox, line_number=0)
    
    pages_a = [PageData(page_number=1, text_blocks=[block_a])]
    pages_b = [PageData(page_number=1, text_blocks=[block_b])]
    
    result = compare_pdfs(pages_a, pages_b, "file_a.pdf", "file_b.pdf")
    
    assert result.pdf_a_path == "file_a.pdf"
    assert result.pdf_b_path == "file_b.pdf"
    assert result.total_pages_a == 1
    assert result.total_pages_b == 1
    assert len(result.diff_items) == 1


def test_compare_pdfs_unequal_pages():
    """Test comparing PDFs with different page counts."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block = TextBlock(text="Text", bounding_box=bbox, line_number=0)
    
    pages_a = [
        PageData(page_number=1, text_blocks=[block]),
        PageData(page_number=2, text_blocks=[block])
    ]
    pages_b = [
        PageData(page_number=1, text_blocks=[block])
    ]
    
    result = compare_pdfs(pages_a, pages_b, "file_a.pdf", "file_b.pdf")
    
    assert result.total_pages_a == 2
    assert result.total_pages_b == 1
    # Should have differences for the extra page
    assert len(result.diff_items) > 0


def test_word_level_diffs():
    """Test that diffs work at word level, not character level."""
    text_a = "Hello this is Michael"
    text_b = "Hello this is Tabatha"
    
    char_diffs = _compute_char_diffs(text_a, text_b)
    
    # Should have equal "Hello this is " and replace "Michael" -> "Tabatha"
    assert len(char_diffs) == 2
    assert char_diffs[0].operation == 'equal'
    assert char_diffs[0].text_a == "Hello this is "
    assert char_diffs[1].operation == 'replace'
    assert char_diffs[1].text_a == "Michael"
    assert char_diffs[1].text_b == "Tabatha"


def test_word_level_insertion():
    """Test word-level diff detects complete word insertions."""
    text_a = "Hello this is Michael"
    text_b = "Hello this is not Michael"
    
    char_diffs = _compute_char_diffs(text_a, text_b)
    
    # Should have equal, insert "not ", equal
    assert len(char_diffs) == 3
    assert char_diffs[0].operation == 'equal'
    assert char_diffs[0].text_a == "Hello this is "
    assert char_diffs[1].operation == 'insert'
    assert char_diffs[1].text_b == "not "
    assert char_diffs[2].operation == 'equal'
    assert char_diffs[2].text_a == "Michael"


def test_operation_inference_insert_only():
    """Test that insert-only changes are classified as insert."""
    text_a = "Tips"
    text_b = "Tips / Other Items"
    
    char_diffs = _compute_char_diffs(text_a, text_b)
    inferred_op = _infer_operation_from_char_diffs(char_diffs)
    
    assert inferred_op == 'insert'


def test_operation_inference_replace():
    """Test that true replacements are classified as replace."""
    text_a = "Vanilla"
    text_b = "Chocolate"
    
    char_diffs = _compute_char_diffs(text_a, text_b)
    inferred_op = _infer_operation_from_char_diffs(char_diffs)
    
    assert inferred_op == 'replace'


def test_operation_inference_ignores_whitespace_replace():
    """Test that whitespace-only replace operations are ignored in classification."""
    text_a = "Line one\nLine two"
    text_b = "Line one Line two"  # newline replaced with space
    
    char_diffs = _compute_char_diffs(text_a, text_b)
    
    # Should have whitespace replace operation
    has_whitespace_replace = any(
        d.operation == 'replace' and 
        d.text_a and d.text_a.strip() == '' and
        d.text_b and d.text_b.strip() == ''
        for d in char_diffs
    )
    assert has_whitespace_replace
    
    # But should not affect classification
    inferred_op = _infer_operation_from_char_diffs(char_diffs)
    # Since all other ops are equal, this is effectively no change (but defaults to replace)
    assert inferred_op == 'replace'


def test_text_reflow_detected_as_insert():
    """Test that text reflow (insert causing line break change) is detected as insert."""
    bbox1 = BoundingBox(x=10, y=20, width=100, height=20)
    bbox2 = BoundingBox(x=10, y=50, width=100, height=20)
    
    # Original: two lines with text split at different point
    block_a1 = TextBlock(text="Hello world this", bounding_box=bbox1, line_number=0)
    block_a2 = TextBlock(text="is text", bounding_box=bbox2, line_number=1)
    
    # Modified: inserted word causes text to wrap differently
    block_b1 = TextBlock(text="Hello world extra this", bounding_box=bbox1, line_number=0)
    block_b2 = TextBlock(text="is text", bounding_box=bbox2, line_number=1)
    
    page_a = PageData(page_number=1, text_blocks=[block_a1, block_a2])
    page_b = PageData(page_number=1, text_blocks=[block_b1, block_b2])
    
    result = compare_pages(page_a, page_b)
    
    # Should detect as insert (word "extra" added), not replace
    # After grouping and re-analysis, should be classified as insert
    assert len(result) >= 1
    # Find the diff item that contains the change
    insert_found = any(item.operation == DiffOperation.INSERT for item in result)
    assert insert_found


def test_spatially_close_diffs_merged():
    """Test that spatially close diff items are merged and re-analyzed."""
    bbox1 = BoundingBox(x=10, y=20, width=100, height=20)
    bbox2 = BoundingBox(x=10, y=50, width=100, height=20)  # 30px gap (< 100px threshold)
    
    # Two consecutive lines that should be grouped
    block_a1 = TextBlock(text="Line one", bounding_box=bbox1, line_number=0)
    block_a2 = TextBlock(text="Line two", bounding_box=bbox2, line_number=1)
    
    block_b1 = TextBlock(text="Line one updated", bounding_box=bbox1, line_number=0)
    block_b2 = TextBlock(text="Line two updated", bounding_box=bbox2, line_number=1)
    
    page_a = PageData(page_number=1, text_blocks=[block_a1, block_a2])
    page_b = PageData(page_number=1, text_blocks=[block_b1, block_b2])
    
    result = compare_pages(page_a, page_b)
    
    # Should be grouped into a single diff item
    assert len(result) == 1
    assert "Line one" in result[0].text_a
    assert "Line two" in result[0].text_a
    assert "\n" in result[0].text_a  # Newline preserved
