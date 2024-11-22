from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

competency_bp = Blueprint('competency_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
competency_collection = db[config.COMPETENCY_COLLECTION_NAME]

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

@competency_bp.route('/')
def index():
    competencies = list(competency_collection.find())
    for doc in competencies:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return jsonify(competencies)

@competency_bp.route('/add', methods=['POST'])
def add_competency():
    data = request.get_json()
    data = parse_dates(data)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data["created_at"]=current_time
    competency_collection.insert_one(data)
    return jsonify({'message': 'Competency added successfully'}), 201

@competency_bp.route('/update', methods=['POST'])
def update_competency():
    data = request.get_json()
    data = parse_dates(data)
    name = data.get('name')

    result = competency_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Competency updated"}), 200
    else:
        return jsonify({"message": "Competency not found"}), 404

@competency_bp.route('/delete', methods=['POST'])
def delete_competency():
    data = request.get_json()
    name = data.get('name')

    result = competency_collection.delete_one({"name": name})
    if result.deleted_count > 0:
        return jsonify({'message': 'Competency deleted successfully'}), 200
    else:
        return jsonify({'message': 'Competency not found'}), 404

@competency_bp.route('/get', methods=['POST'])
def get_competency():
    data = request.get_json()
    name = data.get('name')
    competency = competency_collection.find_one({"name": name})

    if competency:
        competency['_id'] = str(competency['_id'])
        for key, value in competency.items():
            if isinstance(value, datetime):
                competency[key] = value.strftime("%Y-%m-%d")
        return jsonify(competency)
    else:
        return jsonify({'message': 'Competency not found'}), 404
