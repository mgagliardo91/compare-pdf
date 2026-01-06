"""Development server runner for the PDF OCR Diff API."""

import uvicorn
from pdf_ocr_diff_api.config import settings


def main():
    """Run the development server."""
    uvicorn.run(
        "pdf_ocr_diff_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
