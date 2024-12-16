from flask import Flask, request, jsonify, send_file
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
API_KEY = 'tnm123'
UPLOAD_FOLDER = '/tmp'
MAX_FILE_SIZE_MB = 2

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def compress_pdf(input_path, output_path):
    """Compress PDF using Ghostscript."""
    command = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/screen',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ]
    subprocess.run(command, check=True)

@app.route('/')
def home():
    return "Welcome to the PDF Compression API!"

@app.route('/compress', methods=['POST'])
def compress():
    # Check API key
    api_key = request.headers.get('x-api-key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # Check if a file is provided
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the file
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    # Compress the PDF
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'compressed_{filename}')
    try:
        compress_pdf(input_path, output_path)
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to compress PDF'}), 500

    # Check the file size
    if os.path.getsize(output_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
        os.remove(output_path)
        return jsonify({'error': 'Compressed file is larger than 2MB'}), 400

    # Send the compressed file back
    return send_file(output_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
