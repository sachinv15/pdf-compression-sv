from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
import os
import tempfile

app = FastAPI()

# API Key configuration
API_KEY = "your-secret-api-key"  # Change this to your desired API key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
    )

# Home endpoint for testing
@app.get("/")
async def home():
    return {"message": "PDF Compression API is running"}

# PDF compression endpoint
@app.post("/compress")
async def compress_pdf(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    # Check if the uploaded file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Create output path
        output_path = os.path.join(temp_dir, f"compressed_{file.filename}")

        try:
            # Read the PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Copy pages with compression
            for page in reader.pages:
                writer.add_page(page)

            # Save with compression
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            # Check if compressed file exists and its size
            if not os.path.exists(output_path):
                raise HTTPException(status_code=500, detail="Compression failed")

            # Check file size (2MB = 2 * 1024 * 1024 bytes)
            if os.path.getsize(output_path) > 2 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Compressed file size is still larger than 2MB"
                )

            # Return the compressed file
            return FileResponse(
                output_path,
                media_type="application/pdf",
                filename=file.filename
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (for Railway deployment)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
