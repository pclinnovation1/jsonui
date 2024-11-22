



from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

performance_role_bp = Blueprint('performance_role_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_role_collection = db[config.PERFORMANCE_ROLE_COLLECTION_NAME]

def parse_dates(data):
    for key, value in data.items():
        if isinstance(value, str) and '-' in value:
            try:
                data[key] = datetime.strptime(value, '%Y-%m-%d')
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

@performance_role_bp.route('/add_role', methods=['POST'])
def add_role():
    data = request.get_json()
    data = lowercase_keys(data)
    data = parse_dates(data)
    data['created_date'] = datetime.utcnow()
    data['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['updated_by'] = data.get('updated_by')

    result = performance_role_collection.insert_one(data)
    return jsonify({"msg": "Role added successfully", "id": str(result.inserted_id)}), 201

@performance_role_bp.route('/update_role', methods=['POST'])
def update_role():
    data = request.get_json()
    data = lowercase_keys(data)
    data = parse_dates(data)
    data['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['updated_by'] = data.get('updated_by')

    name = data.get('name')
    result = performance_role_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"msg": "Role updated successfully"}), 200
    else:
        return jsonify({"msg": "Role not found"}), 404

@performance_role_bp.route('/get_roles', methods=['POST'])
def get_roles():
    data = request.get_json()
    data = lowercase_keys(data)

    query = {key: value for key, value in data.items() if key in ['name', 'status']}

    roles = list(performance_role_collection.find(query))
    for role in roles:
        role['_id'] = str(role['_id'])  # Convert ObjectId to string
        for key, value in role.items():
            if isinstance(value, datetime):
                role[key] = value.isoformat() + 'Z'

    return jsonify(roles), 200








