from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

questionnaire_bp = Blueprint('questionnaire_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
questionnaire_collection = db[config.QUESTIONNAIRE_COLLECTION_NAME]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

@questionnaire_bp.route('/add', methods=['POST'])
def add_questionnaire():
    data = request.get_json()
    data = lowercase_keys(data)

    result = questionnaire_collection.insert_one(data)
    return jsonify({"message": "Questionnaire template added", "id": str(result.inserted_id)}), 201

@questionnaire_bp.route('/update', methods=['POST'])
def update_questionnaire():
    data = request.get_json()
    data = lowercase_keys(data)
    name = data.get('name')

    data['updated_date'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    result = questionnaire_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Questionnaire template updated"}), 200
    else:
        return jsonify({"message": "Questionnaire template not found"}), 404

@questionnaire_bp.route('/get', methods=['POST'])
def get_questionnaire():
    data = request.get_json()
    name = data.get('name')
    template = questionnaire_collection.find_one({"name": name})

    if template:
        template['_id'] = str(template['_id'])
        return jsonify(template)
    else:
        return jsonify({"message": "Questionnaire template not found"}), 404

@questionnaire_bp.route('/delete', methods=['POST'])
def delete_questionnaire():
    data = request.get_json()
    name = data.get('name')

    result = questionnaire_collection.delete_one({"name": name})
    if result.deleted_count > 0:
        return jsonify({"message": "Questionnaire template deleted successfully"}), 200
    else:
        return jsonify({"message": "Questionnaire template not found"}), 404
