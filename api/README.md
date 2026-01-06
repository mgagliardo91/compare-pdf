# PDF OCR Diff API

Production-ready FastAPI service for comparing PDF documents using OCR and spatial diff analysis.

## Features

- **RESTful API**: Simple HTTP endpoints for PDF comparison
- **Health checks**: `/healthz` endpoint for monitoring
- **Production-ready**: CORS, security headers, error handling, structured logging
- **OpenAPI docs**: Auto-generated documentation at `/docs`
- **File validation**: Type and size validation for uploaded PDFs
- **Request tracing**: Unique request IDs for all operations

## Installation

**Important:** The API depends on the core library, so install core first.

1. Install the core library:
```bash
cd core
pip install -e .
```

2. Navigate to the api directory:
```bash
cd ../api
```

3. Create and activate a virtual environment (recommended, if not already active):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install the API package:
```bash
pip install -e .
```

## Running the API

### Development Server

Run with auto-reload enabled:
```bash
python server.py
```

Or using uvicorn directly:
```bash
uvicorn pdf_ocr_diff_api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production Server

For production, use a production ASGI server with multiple workers:
```bash
uvicorn pdf_ocr_diff_api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```bash
GET /healthz
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Example:**
```bash
curl http://localhost:8000/healthz
```

### Compare PDFs

```bash
POST /v1/diff
```

**Parameters:**
- `file_a` (required): First PDF file to compare
- `file_b` (required): Second PDF file to compare  
- `dpi` (optional): DPI resolution for PDF rendering (default: 300, range: 72-600)

**Response:**
```json
{
  "pdf_a_path": "document1.pdf",
  "pdf_b_path": "document2.pdf",
  "total_pages_a": 5,
  "total_pages_b": 5,
  "total_differences": 12,
  "diff_items": [
    {
      "operation": "replace",
      "page_a": 1,
      "page_b": 1,
      "text_a": "Original text",
      "text_b": "Modified text",
      "bounding_boxes_a": [
        {
          "x": 100,
          "y": 200,
          "width": 300,
          "height": 50
        }
      ],
      "bounding_boxes_b": [
        {
          "x": 100,
          "y": 200,
          "width": 320,
          "height": 50
        }
      ],
      "unified_diff": "--- page_1\n+++ page_1\n@@ -1 +1 @@\n-Original text\n+Modified text",
      "char_diffs": [
        {
          "operation": "replace",
          "text_a": "Original",
          "text_b": "Modified",
          "start_a": 0,
          "end_a": 8,
          "start_b": 0,
          "end_b": 8
        }
      ]
    }
  ]
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/v1/diff \
  -F "file_a=@path/to/document1.pdf" \
  -F "file_b=@path/to/document2.pdf" \
  -F "dpi=300"
```

**Example with Python:**
```python
import requests

url = "http://localhost:8000/v1/diff"

files = {
    "file_a": open("document1.pdf", "rb"),
    "file_b": open("document2.pdf", "rb"),
}
data = {
    "dpi": 300
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Example with JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('file_a', fileA);  // File object
formData.append('file_b', fileB);  // File object
formData.append('dpi', '300');

const response = await fetch('http://localhost:8000/v1/diff', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

## Configuration

Configuration is managed via environment variables with the prefix `PDF_DIFF_`:

```bash
# Server Configuration
PDF_DIFF_HOST=0.0.0.0
PDF_DIFF_PORT=8000
PDF_DIFF_DEBUG=false

# CORS Configuration
PDF_DIFF_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# File Upload Configuration
PDF_DIFF_MAX_FILE_SIZE=52428800  # 50MB in bytes

# Logging Configuration
PDF_DIFF_LOG_LEVEL=INFO
```

Create a `.env` file in the api directory to set these values.

## Project Structure

```
api/
├── pdf_ocr_diff_api/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # FastAPI app with middleware
│   ├── routes.py         # API endpoint handlers
│   ├── models.py         # Pydantic request/response models
│   └── config.py         # Configuration settings
├── server.py             # Development server runner
├── pyproject.toml        # Package dependencies
└── README.md             # This file
```

## Development

### Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Try out endpoints directly in the browser
  - See request/response schemas
  
- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation view
  - Better for reading

### Adding New Endpoints

1. Define request/response models in `models.py`
2. Add route handler in `routes.py`
3. The endpoint will automatically appear in `/docs`

### Security Features

- **CORS**: Configurable allowed origins
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS
- **Request Tracing**: Unique X-Request-ID header for all requests
- **Error Handling**: Global exception handler with structured error responses
- **Input Validation**: Pydantic models for request validation

## Next Steps

The API is currently set up with mock responses. To integrate the actual PDF diff logic:

1. Add the pdf_ocr_diff package as a dependency to `pyproject.toml`
2. Update the `/v1/diff` endpoint in `routes.py` to:
   - Save uploaded files to temporary storage
   - Call the pdf_ocr_diff functions
   - Return the actual diff results
   - Clean up temporary files

## License

MIT
