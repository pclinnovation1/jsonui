


from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

feedback_template_bp = Blueprint('feedback_template_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
feedback_templates_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
questionnaires_collection = db[config.QUESTIONNAIRE_COLLECTION_NAME]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

# Route to create a new feedback template
@feedback_template_bp.route('/create', methods=['POST'])
def create_feedback_template():
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores

    # Fetch the questions from the P_Questionnaires collection
    questionnaire_name = data.get('questionnaire_name')
    if questionnaire_name:
        questionnaire = questionnaires_collection.find_one({'name': questionnaire_name})
        if questionnaire:
            data['questions'] = questionnaire.get('questions', [])
        else:
            return jsonify({'error': 'Questionnaire not found'}), 404

    result = feedback_templates_collection.insert_one(data)
    new_feedback_template = feedback_templates_collection.find_one({'_id': result.inserted_id})
    new_feedback_template['_id'] = str(new_feedback_template['_id'])
    return jsonify(new_feedback_template), 201

# Route to update a feedback template
@feedback_template_bp.route('/update/<template_name>', methods=['POST'])
def update_feedback_template(template_name):
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores

    # Fetch the questions from the P_Questionnaires collection
    questionnaire_name = data.get('questionnaire_name')
    if questionnaire_name:
        questionnaire = questionnaires_collection.find_one({'name': questionnaire_name})
        if questionnaire:
            data['questions'] = questionnaire.get('questions', [])
        else:
            return jsonify({'error': 'Questionnaire not found'}), 404

    result = feedback_templates_collection.update_one({'name': template_name}, {'$set': data})
    if result.matched_count:
        updated_feedback_template = feedback_templates_collection.find_one({'name': template_name})
        updated_feedback_template['_id'] = str(updated_feedback_template['_id'])
        return jsonify(updated_feedback_template), 200
    else:
        return jsonify({'error': 'Feedback template not found'}), 404

# Route to delete a feedback template
@feedback_template_bp.route('/delete/<template_name>', methods=['POST'])
def delete_feedback_template(template_name):
    result = feedback_templates_collection.delete_one({'name': template_name})
    if result.deleted_count:
        return jsonify({'message': 'Feedback template deleted successfully'}), 200
    else:
        return jsonify({'error': 'Feedback template not found'}), 404
