from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId

process_bp = Blueprint('process_bp', __name__)

@process_bp.route('/', methods=['POST'])
def create_process():
    data = request.get_json()
    print("Process contoller")
    process = {
        "processId": str(ObjectId()),
        "name": data['name'],
        "description": data['description']
    }
    current_app.mongo.db.processes.insert_one(process)
    
    # Convert ObjectId to string before returning
    process['_id'] = str(process['_id'])
    
    return jsonify({"message": "Process created", "process": process}), 201
