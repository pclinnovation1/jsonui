from flask import Flask, request, jsonify, send_file
from jinja2 import Template
from fpdf import FPDF
from pymongo import MongoClient
import json
import os

app = Flask(__name__)

# Define the file paths directly in the code
TEMPLATE_JSON_PATH = r"C:\Users\hp\OneDrive\Documents\Desktop\PCL\certificate_generation\test-json.json"
CONFIG_JSON_PATH = r"C:\Users\hp\OneDrive\Documents\Desktop\PCL\certificate_generation\config.json"
OUTPUT_DIR_PATH = r"C:\Users\hp\OneDrive\Documents\Desktop\PCL\certificate_generation\output_pdfs"

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "testing_db"
MONGO_COLLECTION = "offer_letter"

# Function to read JSON file
def read_json_file(json_path):
    print(f"Reading JSON file from: {json_path}")
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        raise

# Function to fetch specific data from MongoDB
def fetch_candidates(query):
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        candidates = list(collection.find(query))
        if candidates:
            print("Fetched candidates from MongoDB:", candidates)
            return candidates
        else:
            raise Exception("No candidates found in MongoDB for the given query")
    except Exception as e:
        print(f"Error fetching candidates from MongoDB: {e}")
        raise

# Function to replace placeholders in the template with data
def fill_template(template_str, data):
    try:
        template = Template(template_str)
        return template.render(data)
    except Exception as e:
        print(f"Error filling template: {e}")
        raise

# Function to create a PDF from text
def create_pdf(text_content, pdf_path):
    print(f"Creating PDF at: {pdf_path}")
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in text_content.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.output(pdf_path)
        print(f"PDF created at {pdf_path}")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        raise

@app.route('/generate_pdfs', methods=['POST'])
def generate_pdfs():
    try:
        # Read query from the request body
        query = request.json
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Fetch data of candidates matching the query from MongoDB
        candidates = fetch_candidates(query)

        # Debug: Print the data fetched from MongoDB
        print("Data received:", candidates)

        # Read the template from the JSON file
        template_json = read_json_file(TEMPLATE_JSON_PATH)

        # Read the config from the JSON file
        config_data = read_json_file(CONFIG_JSON_PATH)

        # Debug: Print the loaded template and config JSON
        print("Template JSON loaded:", template_json)
        print("Config JSON loaded:", config_data)

        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR_PATH, exist_ok=True)

        # Generate a separate PDF for each candidate
        for candidate in candidates:
            # Merge candidate data with config data
            candidate_data = {**config_data, **candidate}

            # Select the appropriate template based on the candidate's status
            if candidate['Status'] == 'Hired':
                template_str = template_json['OfferLetterTemplate']['body']
            elif candidate['Status'] == 'Rejected':
                template_str = template_json['JobRejectionLetterTemplate']['body']
            else:
                continue  # Skip if the status is neither 'Hired' nor 'Rejected'

            # Fill the template with merged data
            populated_template = fill_template(template_str, candidate_data)
            candidate_name = candidate['Candidate_Name'].replace(" ", "_")
            pdf_path = os.path.join(OUTPUT_DIR_PATH, f"{candidate_name}_{candidate['Status']}_Letter.pdf")
            create_pdf(populated_template, pdf_path)
            print(f"{candidate['Status']} letter generated for: {candidate['Candidate_Name']}")

        # Return a success message
        return jsonify({"message": "Letters generated successfully."})

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
