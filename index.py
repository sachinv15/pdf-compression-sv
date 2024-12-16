from fastapi import FastAPI, File, UploadFile
import os
import subprocess

app = FastAPI()

input_folder = 'To Compress'
output_folder = 'Compressed'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

@app.post("/compress-pdf/")
async def compress_pdf(file: UploadFile = File(...)):
    input_path = os.path.join(input_folder, file.filename)
    output_path = os.path.join(output_folder, file.filename)

    # Save the uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Compress the PDF using Ghostscript
    subprocess.call(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                     '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     '-sOutputFile=' + output_path, input_path])

    return {"filename": file.filename, "output_path": output_path}
