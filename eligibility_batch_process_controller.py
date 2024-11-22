


from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

eligibility_batch_process_bp = Blueprint('eligibility_batch_process_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
eligibility_batch_process_collection = db[config.ELIGIBILITY_BATCH_PROCESS_COLLECTION_NAME]

# Helper function to parse date strings into datetime objects
def parse_dates(data):
    for key, value in data.items():
        if isinstance(value, str) and "T" in value:
            try:
                data[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                pass
        elif isinstance(value, dict) and '$date' in value:
            data[key] = datetime.strptime(value['$date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return data

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

@eligibility_batch_process_bp.route('/add', methods=['POST'])
def add_document():
    data = request.get_json()
    data = lowercase_keys(data)
    data = parse_dates(data)

    result = eligibility_batch_process_collection.insert_one(data)
    return jsonify({"message": "Document added", "id": str(result.inserted_id)}), 201

@eligibility_batch_process_bp.route('/update', methods=['POST'])
def update_document():
    data = request.get_json()
    data = lowercase_keys(data)
    data = parse_dates(data)
    document_name = data.get('performance_document_name')

    result = eligibility_batch_process_collection.update_one({"performance_document_name": document_name}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Document updated"}), 200
    else:
        return jsonify({"message": "Document not found"}), 404

@eligibility_batch_process_bp.route('/delete', methods=['POST'])
def delete_document():
    data = request.get_json()
    data = lowercase_keys(data)
    document_name = data.get('performance_document_name')

    result = eligibility_batch_process_collection.delete_one({"performance_document_name": document_name})
    if result.deleted_count > 0:
        return jsonify({"message": "Document deleted successfully"}), 200
    else:
        return jsonify({"message": "Document not found"}), 404

@eligibility_batch_process_bp.route('/get', methods=['POST'])
def get_document():
    data = request.get_json()
    data = lowercase_keys(data)
    document_name = data.get('performance_document_name')
    document = eligibility_batch_process_collection.find_one({"performance_document_name": document_name})

    if document:
        document['_id'] = str(document['_id'])
        for key, value in document.items():
            if isinstance(value, datetime):
                document[key] = {"$date": value.isoformat() + 'Z'}
        return jsonify(document)
    else:
        return jsonify({"message": "Document not found"}), 404











