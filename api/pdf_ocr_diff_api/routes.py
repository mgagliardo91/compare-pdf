"""API route handlers."""

import logging
import tempfile
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from pdf_ocr_diff.ocr import process_pdf
from pdf_ocr_diff.differ import compare_pdfs as compare_pdfs_core

from .models import HealthResponse, DiffResponse, BoundingBox, CharDiff, DiffItem
from .config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the API status and version.
    """
    return HealthResponse(status="healthy", version=settings.app_version)


@router.post("/v1/diff", response_model=DiffResponse, tags=["Diff"])
async def compare_pdfs(
    file_a: UploadFile = File(..., description="First PDF file to compare"),
    file_b: UploadFile = File(..., description="Second PDF file to compare"),
    dpi: int = Form(300, description="DPI for PDF rendering (default: 300)"),
):
    """
    Compare two PDF files and return differences.

    Args:
        file_a: First PDF file
        file_b: Second PDF file
        dpi: DPI resolution for PDF rendering (default: 300)

    Returns:
        DiffResponse with comparison results

    Raises:
        HTTPException: If file validation fails or processing error occurs
    """
    # Validate file types
    if not file_a.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for file_a: {file_a.filename}. Only PDF files are allowed.",
        )

    if not file_b.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for file_b: {file_b.filename}. Only PDF files are allowed.",
        )

    # Validate DPI
    if dpi < 72 or dpi > 600:
        raise HTTPException(status_code=400, detail="DPI must be between 72 and 600")

    # Log the diff operation
    logger.info(f"Diffing PDFs: {file_a.filename} vs {file_b.filename} at {dpi} DPI")

    # Create temporary files for uploaded PDFs
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Save uploaded files
        pdf_a_path = temp_path / file_a.filename
        pdf_b_path = temp_path / file_b.filename
        
        try:
            # Write files to disk
            with open(pdf_a_path, "wb") as f:
                content = await file_a.read()
                f.write(content)
            
            with open(pdf_b_path, "wb") as f:
                content = await file_b.read()
                f.write(content)
            
            logger.info(f"Processing PDF A: {pdf_a_path}")
            pages_a = process_pdf(str(pdf_a_path), dpi=dpi)
            
            logger.info(f"Processing PDF B: {pdf_b_path}")
            pages_b = process_pdf(str(pdf_b_path), dpi=dpi)
            
            logger.info(f"Comparing documents...")
            result = compare_pdfs_core(
                pages_a,
                pages_b,
                file_a.filename,
                file_b.filename,
            )
            
            # Convert core DiffResult to API DiffResponse
            diff_items = []
            for item in result.diff_items:
                # Convert bounding boxes
                bboxes_a = [
                    BoundingBox(
                        x=bbox.x,
                        y=bbox.y,
                        width=bbox.width,
                        height=bbox.height
                    )
                    for bbox in item.bounding_boxes_a
                ]
                
                bboxes_b = [
                    BoundingBox(
                        x=bbox.x,
                        y=bbox.y,
                        width=bbox.width,
                        height=bbox.height
                    )
                    for bbox in item.bounding_boxes_b
                ]
                
                # Convert char diffs
                char_diffs = [
                    CharDiff(
                        operation=cd.operation,
                        text_a=cd.text_a,
                        text_b=cd.text_b,
                        start_a=cd.start_a,
                        end_a=cd.end_a,
                        start_b=cd.start_b,
                        end_b=cd.end_b
                    )
                    for cd in item.char_diffs
                ]
                
                diff_items.append(
                    DiffItem(
                        operation=item.operation.value,
                        page_a=item.page_a,
                        page_b=item.page_b,
                        text_a=item.text_a,
                        text_b=item.text_b,
                        bounding_boxes_a=bboxes_a,
                        bounding_boxes_b=bboxes_b,
                        unified_diff=item.unified_diff,
                        char_diffs=char_diffs
                    )
                )
            
            response = DiffResponse(
                pdf_a_path=result.pdf_a_path,
                pdf_b_path=result.pdf_b_path,
                total_pages_a=result.total_pages_a,
                total_pages_b=result.total_pages_b,
                total_differences=len(result.diff_items),
                diff_items=diff_items,
            )
            
            logger.info(
                f"Diff completed: {response.total_differences} differences found"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing PDFs: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing PDFs: {str(e)}"
            )
