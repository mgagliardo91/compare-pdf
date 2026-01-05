"""Data models for PDF OCR diff operations."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DiffOperation(Enum):
    """Types of diff operations."""
    EQUAL = "equal"
    DELETE = "delete"
    INSERT = "insert"
    REPLACE = "replace"


@dataclass
class BoundingBox:
    """Represents a rectangular region on a page."""
    x: int
    y: int
    width: int
    height: int

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }


@dataclass
class TextBlock:
    """Represents a block of text with its location on a page."""
    text: str
    bounding_box: BoundingBox
    line_number: int = 0

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "bounding_box": self.bounding_box.to_dict(),
            "line_number": self.line_number
        }


@dataclass
class PageData:
    """Represents OCR data for a single page."""
    page_number: int
    text_blocks: List[TextBlock]
    image_width: int = 0
    image_height: int = 0

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "page_number": self.page_number,
            "text_blocks": [block.to_dict() for block in self.text_blocks],
            "image_width": self.image_width,
            "image_height": self.image_height
        }


@dataclass
class CharDiff:
    """Represents character-level differences within text."""
    operation: str  # 'equal', 'delete', 'insert', 'replace'
    text_a: Optional[str]
    text_b: Optional[str]
    start_a: int  # Character position in text_a
    end_a: int
    start_b: int  # Character position in text_b
    end_b: int

    def to_dict(self):
        return {
            "operation": self.operation,
            "text_a": self.text_a,
            "text_b": self.text_b,
            "start_a": self.start_a,
            "end_a": self.end_a,
            "start_b": self.start_b,
            "end_b": self.end_b
        }


@dataclass
class DiffItem:
    """Represents a single difference between two PDFs."""
    operation: DiffOperation
    page_a: Optional[int]
    page_b: Optional[int]
    text_a: Optional[str]
    text_b: Optional[str]
    bounding_boxes_a: List[BoundingBox] = field(default_factory=list)
    bounding_boxes_b: List[BoundingBox] = field(default_factory=list)
    unified_diff: Optional[str] = None  # Unified diff format
    char_diffs: List[CharDiff] = field(default_factory=list)  # Character-level changes

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        result = {
            "operation": self.operation.value,
            "page_a": self.page_a,
            "page_b": self.page_b,
            "text_a": self.text_a,
            "text_b": self.text_b,
            "bounding_boxes_a": [bbox.to_dict() for bbox in self.bounding_boxes_a],
            "bounding_boxes_b": [bbox.to_dict() for bbox in self.bounding_boxes_b]
        }
        if self.unified_diff:
            result["unified_diff"] = self.unified_diff
        if self.char_diffs:
            result["char_diffs"] = [cd.to_dict() for cd in self.char_diffs]
        return result


@dataclass
class DiffResult:
    """Complete result of comparing two PDFs."""
    pdf_a_path: str
    pdf_b_path: str
    total_pages_a: int
    total_pages_b: int
    diff_items: List[DiffItem]

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "pdf_a_path": self.pdf_a_path,
            "pdf_b_path": self.pdf_b_path,
            "total_pages_a": self.total_pages_a,
            "total_pages_b": self.total_pages_b,
            "total_differences": len(self.diff_items),
            "diff_items": [item.to_dict() for item in self.diff_items]
        }
