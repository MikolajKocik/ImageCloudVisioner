# Image Cloud Visioner

FastAPI-based service that analyzes images using Azure Cognitive Services, performs OCR, removes backgrounds, and converts images to PDF. Ships with a Dockerfile and a simple REST API with OpenAPI docs.

## Features
- Image analysis via Azure Computer Vision (structured insights).
- OCR to extract text from images.
- Background removal returning a transparent PNG.
- Image-to-PDF conversion (JPG/PNG/BMP/TIFF).
- CORS enabled; OpenAPI/Swagger UI available at /docs.

## Tech Stack
- FastAPI + Uvicorn
- Azure Cognitive Services (Computer Vision)
- Pillow (PIL) for image processing
- Python 3.9
- Docker-ready

## Directory Structure (excerpt)
```
.
├─ Dockerfile
├─ requirements.txt
└─ src/
   ├─ main.py
   ├─ endpoints/
   │  └─ image.py
   └─ services/
      ├─ image_process_service.py          # analyze_image, recognize_image (uses Azure CV)
      ├─ remove_background_service.py      # remove_background
      └─ convert_to_pdf_service.py         # convert_to_pdf (Pillow)
```

## Quick Start (Local)

1) Prerequisites
- Python 3.9+
- Azure Cognitive Services (Computer Vision) resource (endpoint + key)
- Optional: Azure identity/Key Vault if your services fetch secrets at runtime
- Make a .env file in project root or src with your configuration (example below)

2) Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3) Configure environment
Create a .env file (paths supported because the app calls load_dotenv()):
```env
# Example variable names — adjust to your service code if they differ
COMPUTER_VISION_ENDPOINT=https://<your-cv-resource>.cognitiveservices.azure.com/
COMPUTER_VISION_KEY=<your_azure_cv_key>

# If you use Azure Identity instead of a static key:
# AZURE_TENANT_ID=...
# AZURE_CLIENT_ID=...
# AZURE_CLIENT_SECRET=...

# If secrets are stored in Key Vault (optional):
# KEY_VAULT_NAME=<your_kv_name>
# CV_ENDPOINT_SECRET_NAME=<secret_name_for_endpoint>
# CV_KEY_SECRET_NAME=<secret_name_for_key>
```

4) Run the API
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
# Open: http://localhost:8080/docs
```

## Quick Start (Docker)

Build and run:
```bash
docker build -t image-cloud-visioner:latest .
docker run --rm -p 8080:8080 \
  -e COMPUTER_VISION_ENDPOINT="https://<your-cv-resource>.cognitiveservices.azure.com/" \
  -e COMPUTER_VISION_KEY="<your_azure_cv_key>" \
  image-cloud-visioner:latest
# Open: http://localhost:8080/docs
```

Alternatively, mount a .env:
```bash
docker run --rm -p 8080:8080 --env-file .env image-cloud-visioner:latest
```

## API Endpoints

Base URL: http://localhost:8080

- GET /
  - Health/info
  - Response: {"message":"Image Cloud Visioner API is running"}

- POST /image/analyze
  - Body: multipart/form-data with file
  - Returns: JSON ImageInsights (structured analysis from Azure CV)
  - Example:
    ```bash
    curl -X POST "http://localhost:8080/image/analyze" \
      -F "file=@sample.jpg"
    ```

- POST /image/ocr
  - Body: multipart/form-data with file
  - Returns: JSON array of strings (recognized text lines/blocks)
  - Example:
    ```bash
    curl -X POST "http://localhost:8080/image/ocr" \
      -F "file=@sample.jpg"
    ```

- POST /image/remove-bg
  - Body: multipart/form-data with file (must be an image MIME type)
  - Returns: image/png (transparent background where applicable)
  - Example:
    ```bash
    curl -X POST "http://localhost:8080/image/remove-bg" \
      -F "file=@sample.png" \
      -o removed-bg.png
    ```

- POST /image/convert
  - Body: multipart/form-data with file
  - Supported formats: .jpg, .png, .bmp, .tiff
  - Returns: application/pdf
  - Example:
    ```bash
    curl -X POST "http://localhost:8080/image/convert" \
      -F "file=@sample.jpg" \
      -o sample.pdf
    ```

Notes:
- OpenAPI documentation: /docs
- CORS is enabled for all origins by default (adjust for production).

## Configuration Notes
- The app loads environment variables via python-dotenv (load_dotenv()).
- Azure Computer Vision credentials can be provided directly (endpoint/key) or via Azure Identity/Key Vault (if implemented in services).
- Ensure your Azure resource (Computer Vision) is in the same region as your data to reduce latency and comply with data residency policies.

## Error Handling
- Validation errors return 400 for unsupported/invalid images.
- Service or timeout issues return appropriate 5xx/504 codes.
- Background removal and conversion perform basic format checks and raise clear error messages.

## Development
- Code style: follow standard Python formatting (e.g., black/ruff if desired).
- Run locally with uvicorn and iterate; hot reload is enabled with --reload.
- Extend ImageInsights and service logic to expose more CV features (tags, categories, objects, captions).

## Security
- Do not commit secrets. Use .env locally and a secrets manager in production.
- Limit keys/permissions; consider Managed Identity and Key Vault for secret-less runtime.
- Validate and sanitize user input; enforce maximum file sizes at ingress/proxy if needed.
