from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

performance_template_bp = Blueprint('performance_template_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
competency_collection = db[config.COMPETENCY_COLLECTION_NAME]
feedback_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]
participant_feedback_collection = db[config.PARTICIPANT_FEEDBACK_COLLECTION]  # Participant feedback collection

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

# Modified fetch_details function to query by 'template_name' for participant feedback
def fetch_details(names, collection, query_field="name"):
    if isinstance(names, list):
        return list(collection.find({query_field: {"$in": names}}))
    else:
        return collection.find_one({query_field: names})

@performance_template_bp.route('/create', methods=['POST'])
def create_template():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON payload found")

        data = lowercase_keys(data)

        competency_names = data.get('competencies', [])
        feedback_name = data.get('feedbacks', '')  # Fetch single feedback by name
        check_in_name = data.get('check_ins', '')  # Fetch single check-in by name
        participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
        
        # Fetch relevant details
        competencies = fetch_details(competency_names, competency_collection)
        feedback = fetch_details(feedback_name, feedback_collection) if feedback_name else None
        check_in = fetch_details(check_in_name, check_in_collection) if check_in_name else None
        participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name") if participant_feedback_name else None

        # Assign the fetched data back to the main data dictionary
        data['competencies'] = competencies if competencies else []
        data['feedbacks'] = feedback if feedback else None
        data['check_ins'] = check_in if check_in else None
        data['participant_feedback'] = participant_feedback

        performance_template_collection.insert_one(data)
        return jsonify({'message': 'Template created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_bp.route('/get', methods=['POST'])
def get_template():
    try:
        data = request.get_json()
        template_name = data.get('name')
        template = performance_template_collection.find_one({"name": template_name})
        
        if template:
            participant_feedback_name = template.get('participant_feedback', {}).get('template_name')
            if participant_feedback_name:
                participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name")
                template['participant_feedback'] = participant_feedback
            
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

        template_name = data.get('name')
        
        competency_names = data.get('competencies', [])
        feedback_name = data.get('feedbacks', '')  # Expecting a single feedback
        check_in_name = data.get('check_ins', '')  # Expecting a single check-in
        participant_feedback_name = data.get('participant_feedback', {}).get('template_name')

        competencies = fetch_details(competency_names, competency_collection)
        feedback = fetch_details(feedback_name, feedback_collection) if feedback_name else None
        check_in = fetch_details(check_in_name, check_in_collection) if check_in_name else None
        participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name") if participant_feedback_name else None

        data['competencies'] = competencies if competencies else []
        data['feedbacks'] = feedback if feedback else None
        data['check_ins'] = check_in if check_in else None
        data['participant_feedback'] = participant_feedback

        result = performance_template_collection.update_one({"name": template_name}, {"$set": data})
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
        template_name = data.get('name')
        
        result = performance_template_collection.delete_one({"name": template_name})
        if result.deleted_count > 0:
            return jsonify({"message": "Template deleted successfully"}), 200
        else:
            return jsonify({"message": "Template not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@performance_template_bp.route('/fetch-details', methods=['POST'])
def fetch_template_details():
    try:
        data = request.get_json()
        competency_names = data.get('competency_name', [])
        feedback_name = data.get('feedback_name', '')
        check_in_name = data.get('check_in_name', '')
        participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
        
        competencies = fetch_details(competency_names, competency_collection)
        feedback = fetch_details(feedback_name, feedback_collection) if feedback_name else None
        check_in = fetch_details(check_in_name, check_in_collection) if check_in_name else None
        participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name") if participant_feedback_name else None
        
        response = {
            "competencies": competencies if isinstance(competencies, list) else [competencies],
            "feedbacks": feedback if feedback else None,
            "check_ins": check_in if check_in else None,
            "participant_feedback": participant_feedback
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
