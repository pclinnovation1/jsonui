from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

performance_document_type_bp = Blueprint('performance_document_type_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_document_type_collection = db[config.PERFORMANCE_DOCUMENT_TYPE_COLLECTION_NAME]

def parse_dates(data):
    for key, value in data.items():
        if isinstance(value, str):
            try:
                data[key] = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                pass
        elif isinstance(value, dict) and '$date' in value:
            data[key] = datetime.strptime(value['$date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return data

@performance_document_type_bp.route('/')
def index():
    document_types = list(performance_document_type_collection.find())
    for doc in document_types:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return jsonify(document_types)

@performance_document_type_bp.route('/add', methods=['POST'])
def add_document_type():
    data = request.get_json()
    data = parse_dates(data)
    
    performance_document_type_collection.insert_one(data)
    return jsonify({'message': 'Document type added successfully'}), 201

@performance_document_type_bp.route('/update', methods=['POST'])
def update_document_type():
    data = request.get_json()
    data = parse_dates(data)
    name = data.get('name')

    result = performance_document_type_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Document type updated"}), 200
    else:
        return jsonify({"message": "Document type not found"}), 404

@performance_document_type_bp.route('/delete', methods=['POST'])
def delete_document_type():
    data = request.get_json()
    name = data.get('name')

    result = performance_document_type_collection.delete_one({"name": name})
    if result.deleted_count > 0:
        return jsonify({'message': 'Document type deleted successfully'}), 200
    else:
        return jsonify({'message': 'Document type not found'}), 404

@performance_document_type_bp.route('/get', methods=['POST'])
def get_document_type():
    data = request.get_json()
    name = data.get('name')
    document_type = performance_document_type_collection.find_one({"name": name})

    if document_type:
        document_type['_id'] = str(document_type['_id'])
        for key, value in document_type.items():
            if isinstance(value, datetime):
                document_type[key] = value.strftime("%Y-%m-%d")
        return jsonify(document_type)
    else:
        return jsonify({'message': 'Document type not found'}), 404
