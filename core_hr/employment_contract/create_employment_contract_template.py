from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://______________")
db = #database name
templates_collection = #template collection

@app.route('/create_template', methods=['POST'])
def create_template():
    data = request.json

    # Extracting the necessary fields from the request
    template_name = data.get('template_name')
    description = data.get('description')
    common = data.get('common')
    specific = data.get('specific')

    # Validation checks
    if not template_name or not common or not specific:
        return jsonify({"error": "template_name, common, and specific fields are required."}), 400

    # Check if a template with the same name already exists
    if templates_collection.find_one({"template_name": template_name}):
        return jsonify({"error": "A template with this name already exists."}), 400

    # Creating the template document
    template = {
        "template_name": template_name,
        "description": description,
        "common": common,
        "specific": specific,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert the template into the collection
    templates_collection.insert_one(template)

    return jsonify({"message": "Template created successfully."}), 201

if __name__ == '__main__':
    app.run(debug=True)
