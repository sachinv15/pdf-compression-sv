from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/compress', methods=['POST'])
def compress_pdf():
    input_folder = 'To Compress'
    output_folder = 'Compressed'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for item in os.listdir(input_folder):
        if item.endswith('.pdf'):
            input_path = os.path.join(input_folder, item)
            output_path = os.path.join(output_folder, item)
            subprocess.call(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                            '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                            '-sOutputFile=' + output_path, input_path])

    return jsonify({"message": "Compression complete"}), 200

if __name__ == '__main__':
    app.run(debug=True)
