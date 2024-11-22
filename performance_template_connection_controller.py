from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

performance_template_connection_bp = Blueprint('performance_template_connection_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_template_collection = db[config.PERFORMANCE_TEMPLATE_CONNECTION_COLLECTION_NAME]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

@performance_template_connection_bp.route('/create', methods=['POST'])
def create_performance_template():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'review_period' not in data or 'performance_document_types' not in data:
            raise ValueError("Missing required fields")

        # Convert keys to lowercase and replace spaces with underscores
        data = lowercase_keys(data)

        performance_template = {
            "name": data['name'],
            "review_period": data['review_period'],
            "performance_document_types": data['performance_document_types']
        }

        performance_template_collection.insert_one(performance_template)
        return jsonify({'message': 'Performance template created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_connection_bp.route('/get', methods=['POST'])
def get_performance_template():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            raise ValueError("No name provided")

        performance_template = performance_template_collection.find_one({"name": name})
        if performance_template:
            performance_template['_id'] = str(performance_template['_id'])
            return jsonify(performance_template), 200
        else:
            return jsonify({"message": "Performance template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_connection_bp.route('/update', methods=['POST'])
def update_performance_template():
    try:
        data = request.get_json()
        data = lowercase_keys(data)
        name = data.get('name')
        if not name:
            raise ValueError("No name provided")

        update_fields = {}
        if 'review_period' in data:
            update_fields['review_period'] = data['review_period']
        if 'performance_document_types' in data:
            update_fields['performance_document_types'] = data['performance_document_types']

        result = performance_template_collection.update_one({"name": name}, {"$set": update_fields})
        if result.matched_count > 0:
            return jsonify({"message": "Performance template updated successfully"}), 200
        else:
            return jsonify({"message": "Performance template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_connection_bp.route('/delete', methods=['POST'])
def delete_performance_template():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            raise ValueError("No name provided")

        result = performance_template_collection.delete_one({"name": name})
        if result.deleted_count > 0:
            return jsonify({"message": "Performance template deleted successfully"}), 200
        else:
            return jsonify({"message": "Performance template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
