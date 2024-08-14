from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

# Blueprint setup
participant_feedback_template_bp = Blueprint('participant_feedback_template_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
participant_feedback_template_collection = db["P_ParticipantFeedbackTemplate"]

@participant_feedback_template_bp.route('/add_participant_feedback_template', methods=['POST'])
def add_participant_feedback_template():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON payload found")

        # Insert the participant feedback template data into the collection
        participant_feedback_template_collection.insert_one(data)
        return jsonify({'message': 'Participant feedback template added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400
