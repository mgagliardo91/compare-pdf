"""API request and response models."""

from pydantic import BaseModel, Field
from typing import List, Optional


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")


class BoundingBox(BaseModel):
    """Bounding box coordinates on a page."""
    x: int = Field(..., description="X coordinate (left)")
    y: int = Field(..., description="Y coordinate (top)")
    width: int = Field(..., description="Width of bounding box")
    height: int = Field(..., description="Height of bounding box")


class CharDiff(BaseModel):
    """Character-level difference within text."""
    operation: str = Field(..., description="Operation type: equal, delete, insert, replace")
    text_a: Optional[str] = Field(None, description="Text from document A")
    text_b: Optional[str] = Field(None, description="Text from document B")
    start_a: int = Field(..., description="Start position in text A")
    end_a: int = Field(..., description="End position in text A")
    start_b: int = Field(..., description="Start position in text B")
    end_b: int = Field(..., description="End position in text B")


class DiffItem(BaseModel):
    """A single difference between two PDFs."""
    operation: str = Field(..., description="Operation type: equal, delete, insert, replace")
    page_a: Optional[int] = Field(None, description="Page number in document A (1-indexed)")
    page_b: Optional[int] = Field(None, description="Page number in document B (1-indexed)")
    text_a: Optional[str] = Field(None, description="Text from document A")
    text_b: Optional[str] = Field(None, description="Text from document B")
    bounding_boxes_a: List[BoundingBox] = Field(default_factory=list, description="Bounding boxes in document A")
    bounding_boxes_b: List[BoundingBox] = Field(default_factory=list, description="Bounding boxes in document B")
    unified_diff: Optional[str] = Field(None, description="Unified diff format")
    char_diffs: List[CharDiff] = Field(default_factory=list, description="Character-level differences")


class DiffResponse(BaseModel):
    """Response model for PDF diff operation."""
    pdf_a_path: str = Field(..., description="Path to document A")
    pdf_b_path: str = Field(..., description="Path to document B")
    total_pages_a: int = Field(..., description="Total pages in document A")
    total_pages_b: int = Field(..., description="Total pages in document B")
    total_differences: int = Field(..., description="Total number of differences found")
    diff_items: List[DiffItem] = Field(default_factory=list, description="List of differences")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
