from flask import Flask, request, jsonify, send_from_directory, url_for
import os
from itsdangerous import URLSafeSerializer

app = Flask(__name__)

# Define the path to the PDF directory
PDF_DIRECTORY = '/home/azureuser/dev1/course_complete_certificate/pdfs/'
SECRET_KEY = 'your_secret_key'  # Change this to a secure key
serializer = URLSafeSerializer(SECRET_KEY)

@app.route('/get-pdf', methods=['POST'])
def get_pdf():
    data = request.get_json()
    pdf_name = data.get('pdf_name')
    
    if not pdf_name:
        return jsonify({"error": "PDF name not provided"}), 400
    
    pdf_path = os.path.join(PDF_DIRECTORY, pdf_name)
    
    if not os.path.isfile(pdf_path):
        return jsonify({"error": "PDF not found"}), 404

    # Generate a secure token
    token = serializer.dumps(pdf_name)
    
    # Generate the downloadable link with the token
    download_url = url_for('download_pdf', token=token, _external=True)
    return jsonify({"download_url": download_url})

@app.route('/download/<token>', methods=['GET'])
def download_pdf(token):
    try:
        # Validate and deserialize the token
        pdf_name = serializer.loads(token)
    except Exception as e:
        return jsonify({"error": "Invalid or expired token"}), 400

    # Ensure the file exists
    pdf_path = os.path.join(PDF_DIRECTORY, pdf_name)
    if not os.path.isfile(pdf_path):
        return jsonify({"error": "PDF not found"}), 404

    return send_from_directory(PDF_DIRECTORY, pdf_name, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
