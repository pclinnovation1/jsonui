


from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

process_flow_bp = Blueprint('process_flow_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
process_flow_collection = db[config.PERFORMANCE_PROCESS_FLOW_COLLECTION_NAME]

# Helper function to parse date strings into datetime objects
def parse_dates(data):
    for key, value in data.items():
        if isinstance(value, str) and '-' in value:
            try:
                data[key] = datetime.strptime(value, "%Y-%m-%d")
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

@process_flow_bp.route('/', methods=['GET'])
def index():
    try:
        process_flows = list(process_flow_collection.find())
        for doc in process_flows:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        return jsonify(process_flows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@process_flow_bp.route('/create', methods=['POST'])
def create_process_flow():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON payload found")
        
        data = lowercase_keys(data)
        data = parse_dates(data)
        
        process_flow_collection.insert_one(data)
        return jsonify({'message': 'Process flow added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
