


from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

performance_template_bp = Blueprint('performance_template_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

@performance_template_bp.route('/create', methods=['POST'])
def create_template():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON payload found")

        data = lowercase_keys(data)

        performance_template_collection.insert_one(data)
        return jsonify({'message': 'Template created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_bp.route('/get', methods=['POST'])
def get_template():
    try:
        data = request.get_json()
        template_name = data.get('general', {}).get('name')
        template = performance_template_collection.find_one({"general.name": template_name})
        
        if template:
            template['_id'] = str(template['_id'])
            return jsonify(template), 200
        else:
            return jsonify({"message": "Template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_bp.route('/update', methods=['POST'])
def update_template():
    try:
        data = request.get_json()
        data = lowercase_keys(data)
        template_name = data.get('general', {}).get('name')
        
        result = performance_template_collection.update_one({"general.name": template_name}, {"$set": data})
        if result.matched_count > 0:
            return jsonify({"message": "Template updated successfully"}), 200
        else:
            return jsonify({"message": "Template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_bp.route('/delete', methods=['POST'])
def delete_template():
    try:
        data = request.get_json()
        template_name = data.get('general', {}).get('name')
        
        result = performance_template_collection.delete_one({"general.name": template_name})
        if result.deleted_count > 0:
            return jsonify({"message": "Template deleted successfully"}), 200
        else:
            return jsonify({"message": "Template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
