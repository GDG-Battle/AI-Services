# AI-Services

## Using pytesseract for OCR

### Installation
1. pip install -r requirements.txt

### Windows-specific steps
1. Download and install Tesseract OCR from [UB Mannheim Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki).
2. During installation, note the installation path (e.g., `C:\Program Files\Tesseract-OCR`).
3. Add the Tesseract installation directory to your system `PATH` environment variable.

## Run project

1. Make sure your `.env` file is set up (e.g. `QDRANT_URL=http://qdrant:6333`).

2. Build and start the containers in detached mode:

```bash
docker compose up -d