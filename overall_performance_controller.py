from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import config

# Define the Blueprint
overall_performance_bp = Blueprint('overall_performance_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
overall_performance_collection = db["P_overall_performance"]

# Function to validate and sanitize input data types
def validate_and_sanitize_data(data):
    if 'overall_summary_and_ratings' in data:
        overall = data['overall_summary_and_ratings']

        # Ensure ratings are integers and descriptions/comments are strings
        for rating_type in ['employee_actual_rating', 'employee_calculated_rating', 'manager_actual_rating', 'manager_calculated_rating']:
            if rating_type in overall:
                overall[rating_type]['rating_scale'] = int(overall[rating_type].get('rating_scale', 0))
                overall[rating_type]['rating'] = int(overall[rating_type].get('rating', 0))
                overall[rating_type]['rating_description'] = str(overall[rating_type].get('rating_description', ""))

                # Only actual ratings have comments
                if 'comments' in overall[rating_type]:
                    overall[rating_type]['comments'] = str(overall[rating_type].get('comments', ""))

        # Ensure all achievements and contributions fields are strings
        if 'achievements_and_contributions' in overall:
            for section in ['achievements', 'contributions']:
                for item in overall['achievements_and_contributions'].get(section, []):
                    item['achievement_name'] = str(item.get('achievement_name', ""))
                    item['description'] = str(item.get('description', ""))
                    item['date'] = str(item.get('date', ""))

# Route to create an overall performance template
@overall_performance_bp.route('/create_overall_performance_template', methods=['POST'])
def create_overall_performance_template():
    try:
        data = request.json

        # Validate and sanitize data
        validate_and_sanitize_data(data)

        # Insert the overall performance template data into the collection
        result = overall_performance_collection.insert_one(data)

        # Convert ObjectId to string for JSON serialization
        data['_id'] = str(result.inserted_id)

        return jsonify({"message": "Overall performance template created successfully", "data": data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to fetch an overall performance template
@overall_performance_bp.route('/get_overall_performance_template', methods=['POST'])
def get_overall_performance_template():
    try:
        data = request.json
        template_id = data.get('_id')

        if not template_id:
            return jsonify({"error": "Missing template ID"}), 400

        template = overall_performance_collection.find_one({"_id": ObjectId(template_id)})

        if not template:
            return jsonify({"error": "Template not found"}), 404

        return jsonify({"data": template}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
