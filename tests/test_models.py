"""Tests for data models and JSON serialization."""

from pdf_ocr_diff.models import (
    BoundingBox, TextBlock, PageData, DiffItem, 
    DiffOperation, DiffResult
)


def test_bounding_box_to_dict():
    """Test BoundingBox serialization."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    result = bbox.to_dict()
    
    assert result == {
        "x": 10,
        "y": 20,
        "width": 100,
        "height": 50
    }


def test_text_block_to_dict():
    """Test TextBlock serialization."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block = TextBlock(text="Hello World", bounding_box=bbox, line_number=1)
    result = block.to_dict()
    
    assert result == {
        "text": "Hello World",
        "bounding_box": {"x": 10, "y": 20, "width": 100, "height": 50},
        "line_number": 1
    }


def test_page_data_to_dict():
    """Test PageData serialization."""
    bbox1 = BoundingBox(x=10, y=20, width=100, height=50)
    bbox2 = BoundingBox(x=10, y=80, width=100, height=50)
    block1 = TextBlock(text="Line 1", bounding_box=bbox1, line_number=0)
    block2 = TextBlock(text="Line 2", bounding_box=bbox2, line_number=1)
    
    page = PageData(
        page_number=1,
        text_blocks=[block1, block2],
        image_width=800,
        image_height=1000
    )
    result = page.to_dict()
    
    assert result["page_number"] == 1
    assert len(result["text_blocks"]) == 2
    assert result["image_width"] == 800
    assert result["image_height"] == 1000


def test_diff_item_to_dict():
    """Test DiffItem serialization."""
    bbox_a = BoundingBox(x=10, y=20, width=100, height=50)
    bbox_b = BoundingBox(x=15, y=25, width=95, height=45)
    
    diff_item = DiffItem(
        operation=DiffOperation.REPLACE,
        page_a=1,
        page_b=1,
        text_a="Old text",
        text_b="New text",
        bounding_boxes_a=[bbox_a],
        bounding_boxes_b=[bbox_b]
    )
    result = diff_item.to_dict()
    
    assert result["operation"] == "replace"
    assert result["page_a"] == 1
    assert result["page_b"] == 1
    assert result["text_a"] == "Old text"
    assert result["text_b"] == "New text"
    assert len(result["bounding_boxes_a"]) == 1
    assert len(result["bounding_boxes_b"]) == 1


def test_diff_result_to_dict():
    """Test DiffResult serialization."""
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    diff_item = DiffItem(
        operation=DiffOperation.INSERT,
        page_a=1,
        page_b=1,
        text_a=None,
        text_b="New text",
        bounding_boxes_a=[],
        bounding_boxes_b=[bbox]
    )
    
    result = DiffResult(
        pdf_a_path="file_a.pdf",
        pdf_b_path="file_b.pdf",
        total_pages_a=5,
        total_pages_b=6,
        diff_items=[diff_item]
    )
    result_dict = result.to_dict()
    
    assert result_dict["pdf_a_path"] == "file_a.pdf"
    assert result_dict["pdf_b_path"] == "file_b.pdf"
    assert result_dict["total_pages_a"] == 5
    assert result_dict["total_pages_b"] == 6
    assert result_dict["total_differences"] == 1
    assert len(result_dict["diff_items"]) == 1
