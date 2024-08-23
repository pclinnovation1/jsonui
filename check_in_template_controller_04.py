from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

check_in_template_bp = Blueprint('check_in_template_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]

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

@check_in_template_bp.route('/add', methods=['POST'])
def add_template():
    data = request.get_json()
    data = lowercase_keys(data)
    data = parse_dates(data)

    result = check_in_collection.insert_one(data)
    return jsonify({"message": "Template added", "id": str(result.inserted_id)}), 201

@check_in_template_bp.route('/update', methods=['POST'])
def update_template():
    data = request.get_json()
    data = lowercase_keys(data)
    data = parse_dates(data)
    name = data.get('name')

    result = check_in_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Template updated"}), 200
    else:
        return jsonify({"message": "Template not found"}), 404

@check_in_template_bp.route('/get', methods=['POST'])
def get_template():
    data = request.get_json()
    name = data.get('name')
    template = check_in_collection.find_one({"name": name})

    if template:
        template['_id'] = str(template['_id'])
        for key, value in template.items():
            if isinstance(value, datetime):
                template[key] = {"$date": value.isoformat() + 'Z'}
        return jsonify(template)
    else:
        return jsonify({"message": "Template not found"}), 404


