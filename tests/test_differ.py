"""Tests for differ module."""

from pdf_ocr_diff.models import (
    BoundingBox, TextBlock, PageData, DiffOperation
)
from pdf_ocr_diff.differ import compare_pages, compare_pdfs


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
