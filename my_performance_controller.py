# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# my_performance_bp = Blueprint('my_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_conn_collection = db[config.PERFORMANCE_TEMPLATE_CONNECTION_COLLECTION_NAME]
# performance_templates_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# goal_plans_collection = db[config.GOAL_PLANS_COLLECTION_NAME]
# my_performance_collection = db[config.MY_PERFORMANCE_COLLECTION_NAME]

# # Function to convert ObjectId and date fields to strings
# def convert_object_id_and_dates(document):
#     if isinstance(document, dict):
#         for key, value in document.items():
#             if isinstance(value, ObjectId):
#                 document[key] = str(value)
#             elif isinstance(value, list):
#                 for item in value:
#                     if isinstance(item, dict):
#                         convert_object_id_and_dates(item)
#             elif isinstance(value, dict):
#                 convert_object_id_and_dates(value)
#             elif hasattr(value, 'isoformat'):
#                 document[key] = value.isoformat()
#     elif isinstance(document, list):
#         for item in document:
#             if isinstance(item, dict):
#                 convert_object_id_and_dates(item)

# # Create a new goal based on provided details
# @my_performance_bp.route('/create_goal', methods=['POST'])
# def create_goal():
#     data = request.json
#     employee_name = data.get('employee_name')
#     performance_document_name = data.get('performance_document_name')
#     name = data.get('name')

#     if not employee_name or not performance_document_name or not name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Find review_period and performance_document_types from the performance template connection collection
#     template_conn = performance_template_conn_collection.find_one(
#         {'name': name},
#         {'review_period': 1, 'performance_document_types': 1}
#     )

#     if not template_conn:
#         return jsonify({"error": f"No entry found for name: {name}"}), 404

#     review_period = template_conn.get('review_period')
#     performance_document_types = template_conn.get('performance_document_types')

#     # Find the relevant goal plans
#     goal_plans = goal_plans_collection.find(
#         {'details.review_period': review_period, 'details.performance_document_types': performance_document_types},
#         {'goals': 1}
#     )

#     goals_list = []
#     for plan in goal_plans:
#         for goal in plan.get('goals', []):
#             goal_entry = {
#                 'goal_name': goal.get('goal_name'),
#                 'employee_rating': None,
#                 'manager_rating': None
#             }
#             goals_list.append(goal_entry)

#     # Fetch additional fields from the performance templates collection
#     performance_template = performance_templates_collection.find_one(
#         {'name': name},
#         {'description': 1, 'competencies': 1, 'feedbacks': 1, 'check_ins': 1}
#     )

#     if not performance_template:
#         return jsonify({"error": f"No performance template found for name: {name}"}), 404

#     # Convert ObjectId and date fields to strings for JSON serialization
#     convert_object_id_and_dates(performance_template)

#     # Add employee and manager ratings to competencies
#     for comp in performance_template.get('competencies', []):
#         comp['employee_rating'] = None
#         comp['manager_rating'] = None

#     # Insert employee's goals and additional fields into my_performance_collection
#     performance_data = {
#         'person_name': employee_name,
#         'performance_document_name': performance_document_name,
#         'goals': goals_list,
#         'description': performance_template.get('description'),
#         'competencies': performance_template.get('competencies', []),
#         'feedbacks': performance_template.get('feedbacks', []),
#         'checkins': performance_template.get('check_ins', [])
#     }

#     result = my_performance_collection.insert_one(performance_data)

#     # Convert ObjectId to string for JSON serialization
#     performance_data['_id'] = str(result.inserted_id)

#     return jsonify({"message": "Goals and additional information added for employee successfully", "data": performance_data}), 201

# # Update an existing goal
# @my_performance_bp.route('/update_goal', methods=['POST'])
# def update_goal():
#     data = request.json
#     employee_name = data.get('employee_name')
#     goal_name = data.get('goal_name')
#     updated_goal = data.get('updated_goal')

#     if not employee_name or not goal_name or not updated_goal:
#         return jsonify({"error": "Missing required parameters"}), 400

#     result = my_performance_collection.update_one(
#         {'employee_name': employee_name, 'goals.goal_name': goal_name},
#         {'$set': {'goals.$': updated_goal}}
#     )

#     if result.matched_count == 0:
#         return jsonify({"error": "Goal not found"}), 404

#     return jsonify({"message": "Goal updated successfully"}), 200

# # Delete a goal
# @my_performance_bp.route('/delete_goal', methods=['POST'])
# def delete_goal():
#     data = request.json
#     employee_name = data.get('employee_name')
#     goal_name = data.get('goal_name')

#     if not employee_name or not goal_name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     result = my_performance_collection.update_one(
#         {'employee_name': employee_name},
#         {'$pull': {'goals': {'goal_name': goal_name}}}
#     )

#     if result.modified_count == 0:
#         return jsonify({"error": "Goal not found or not deleted"}), 404

#     return jsonify({"message": "Goal deleted successfully"}), 200


















































# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# my_performance_bp = Blueprint('my_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_conn_collection = db[config.PERFORMANCE_TEMPLATE_CONNECTION_COLLECTION_NAME]
# performance_templates_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# goal_plans_collection = db[config.GOAL_PLANS_COLLECTION_NAME]
# my_performance_collection = db[config.MY_PERFORMANCE_COLLECTION_NAME]

# # Function to convert ObjectId and date fields to strings
# def convert_object_id_and_dates(document):
#     if isinstance(document, dict):
#         for key, value in document.items():
#             if isinstance(value, ObjectId):
#                 document[key] = str(value)
#             elif isinstance(value, list):
#                 for item in value:
#                     if isinstance(item, dict):
#                         convert_object_id_and_dates(item)
#             elif isinstance(value, dict):
#                 convert_object_id_and_dates(value)
#             elif hasattr(value, 'isoformat'):
#                 document[key] = value.isoformat()
#     elif isinstance(document, list):
#         for item in document:
#             if isinstance(item, dict):
#                 convert_object_id_and_dates(item)

# @my_performance_bp.route('/create_goal', methods=['POST'])
# def create_goal():
#     data = request.json
#     employee_name = data.get('employee_name')
#     performance_document_name = data.get('performance_document_name')
#     name = data.get('name')

#     if not employee_name or not performance_document_name or not name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Find review_period and performance_document_types from the performance template connection collection
#     template_conn = performance_template_conn_collection.find_one(
#         {'name': name, 'performance_document_types': performance_document_name},
#         {'review_period': 1, 'performance_document_types': 1}
#     )

#     if not template_conn:
#         return jsonify({"error": f"No entry found for name: {name} and performance_document_name: {performance_document_name}"}), 404

#     review_period = template_conn.get('review_period')

#     # Find the relevant goal plans
#     goal_plans = goal_plans_collection.find(
#         {'details.review_period': review_period, 'details.performance_document_types': performance_document_name},
#         {'goals': 1}
#     )

#     goals_list = []
#     for plan in goal_plans:
#         for goal in plan.get('goals', []):
#             goal_entry = {
#                 'goal_name': goal.get('goal_name'),
#                 'employee_rating': None,
#                 'manager_rating': None
#             }
#             goals_list.append(goal_entry)

#     # Fetch additional fields from the performance templates collection
#     performance_template = performance_templates_collection.find_one(
#         {'name': name},
#         {'description': 1, 'competencies': 1, 'feedbacks': 1, 'check_ins': 1, 'participant_feedback': 1}
#     )

#     if not performance_template:
#         return jsonify({"error": f"No performance template found for name: {name}"}), 404

#     # Convert ObjectId and date fields to strings for JSON serialization
#     convert_object_id_and_dates(performance_template)

#     # Add employee and manager ratings to competencies
#     for comp in performance_template.get('competencies', []):
#         comp['employee_rating'] = None
#         comp['manager_rating'] = None

#     # Insert employee's goals and additional fields into my_performance_collection
#     performance_data = {
#         'person_name': employee_name,
#         'performance_document_name': performance_document_name,
#         'goals': goals_list,
#         'description': performance_template.get('description'),
#         'competencies': performance_template.get('competencies', []),
#         'feedbacks': performance_template.get('feedbacks', []),
#         'checkins': performance_template.get('check_ins', []),
#         'participant_feedback': performance_template.get('participant_feedback', {}),
#         'review_period': review_period  # Include the review period in the performance document
#     }

#     result = my_performance_collection.insert_one(performance_data)

#     # Convert ObjectId to string for JSON serialization
#     performance_data['_id'] = str(result.inserted_id)

#     return jsonify({"message": "Goals and additional information added for employee successfully", "data": performance_data}), 201







from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config
from bson import ObjectId

# Define the Blueprint
my_performance_bp = Blueprint('my_performance_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_template_conn_collection = db[config.PERFORMANCE_TEMPLATE_CONNECTION_COLLECTION_NAME]
performance_templates_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
goal_plans_collection = db[config.GOAL_PLANS_COLLECTION_NAME]
my_performance_collection = db[config.MY_PERFORMANCE_COLLECTION_NAME]
overall_performance_collection = db["P_overall_performance"]  # Collection for overall performance

# Function to convert ObjectId and date fields to strings
def convert_object_id_and_dates(document):
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_object_id_and_dates(item)
            elif isinstance(value, dict):
                convert_object_id_and_dates(value)
            elif hasattr(value, 'isoformat'):
                document[key] = value.isoformat()
    elif isinstance(document, list):
        for item in document:
            if isinstance(item, dict):
                convert_object_id_and_dates(item)

# @my_performance_bp.route('/create_goal', methods=['POST'])
# def create_goal():
#     data = request.json
#     employee_name = data.get('employee_name')
#     performance_document_name = data.get('performance_document_name')
#     name = data.get('name')

#     if not employee_name or not performance_document_name or not name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Find review_period and performance_document_types from the performance template connection collection
#     template_conn = performance_template_conn_collection.find_one(
#         {'name': name, 'performance_document_types': performance_document_name},
#         {'review_period': 1, 'performance_document_types': 1}
#     )

#     if not template_conn:
#         return jsonify({"error": f"No entry found for name: {name} and performance_document_name: {performance_document_name}"}), 404

#     review_period = template_conn.get('review_period')

#     # Find the relevant goal plans
#     goal_plans = goal_plans_collection.find(
#         {'details.review_period': review_period, 'details.performance_document_types': performance_document_name},
#         {'goals': 1}
#     )

#     goals_list = []
#     for plan in goal_plans:
#         for goal in plan.get('goals', []):
#             goal_entry = {
#                 'goal_name': goal.get('goal_name'),
#                 'employee_rating': None,
#                 'manager_rating': None
#             }
#             goals_list.append(goal_entry)

#     # Fetch additional fields from the performance templates collection
#     performance_template = performance_templates_collection.find_one(
#         {'name': name},
#         {'description': 1, 'competencies': 1, 'feedbacks': 1, 'check_ins': 1, 'participant_feedback': 1}
#     )

#     if not performance_template:
#         return jsonify({"error": f"No performance template found for name: {name}"}), 404

#     # Convert ObjectId and date fields to strings for JSON serialization
#     convert_object_id_and_dates(performance_template)

#     # Add employee and manager ratings to competencies
#     for comp in performance_template.get('competencies', []):
#         comp['employee_rating'] = None
#         comp['manager_rating'] = None

#     # Fetch the overall performance template (assuming a single document exists)
#     overall_performance = overall_performance_collection.find_one({}, {'overall_summary_and_ratings': 1})

#     if not overall_performance:
#         return jsonify({"error": "No overall performance template found in P_overall_performance collection"}), 404

#     # Convert ObjectId and date fields in overall_performance
#     convert_object_id_and_dates(overall_performance)

#     # Insert employee's goals, additional fields, and overall performance into my_performance_collection
#     performance_data = {
#         'person_name': employee_name,
#         'performance_document_name': performance_document_name,
#         'goals': goals_list,
#         'description': performance_template.get('description'),
#         'competencies': performance_template.get('competencies', []),
#         'feedbacks': performance_template.get('feedbacks', []),
#         'checkins': performance_template.get('check_ins', []),
#         'participant_feedback': performance_template.get('participant_feedback', {}),
#         'review_period': review_period,  # Include the review period in the performance document
#         'overall_summary_and_ratings': overall_performance.get('overall_summary_and_ratings', {})
#     }

#     result = my_performance_collection.insert_one(performance_data)

#     # Convert ObjectId to string for JSON serialization
#     performance_data['_id'] = str(result.inserted_id)

#     return jsonify({"message": "Goals and additional information added for employee successfully", "data": performance_data}), 201

@my_performance_bp.route('/create_goal', methods=['POST'])
def create_goal():
    data = request.json
    employee_name = data.get('employee_name')
    performance_document_name = data.get('performance_document_name')
    name = data.get('name')

    if not employee_name or not performance_document_name or not name:
        return jsonify({"error": "Missing required parameters"}), 400

    # Find review_period and performance_document_types from the performance template connection collection
    template_conn = performance_template_conn_collection.find_one(
        {'name': name, 'performance_document_types': performance_document_name},
        {'review_period': 1, 'performance_document_types': 1}
    )

    if not template_conn:
        return jsonify({"error": f"No entry found for name: {name} and performance_document_name: {performance_document_name}"}), 404

    review_period = template_conn.get('review_period')

    # Find the relevant goal plans
    goal_plans = goal_plans_collection.find(
        {'details.review_period': review_period, 'details.performance_document_types': performance_document_name},
        {'goals': 1}
    )

    goals_list = []
    for plan in goal_plans:
        for goal in plan.get('goals', []):
            goal_entry = {
                'goal_name': goal.get('goal_name'),
                'employee_rating': None,
                'manager_rating': None
            }
            goals_list.append(goal_entry)

    # Fetch additional fields from the performance templates collection
    performance_template = performance_templates_collection.find_one(
        {'name': name},
        {'description': 1, 'competencies': 1, 'feedbacks': 1, 'check_ins': 1, 'participant_feedback': 1}
    )

    if not performance_template:
        return jsonify({"error": f"No performance template found for name: {name}"}), 404
    
    print("performance_template  : ", performance_template)
    print() 

    # Fetch the participant feedback template if it exists
    participant_feedback_template = performance_template.get('participant_feedback')
    print("participant_feedback_template  : ", participant_feedback_template)
    print()
    if participant_feedback_template:
        participant_feedback = db.P_ParticipantFeedbackTemplate.find_one(
            {'template_name': participant_feedback_template.get('template_name')}
        )
        print(" participant_feedback : ",participant_feedback )
        print()
        if participant_feedback:
            convert_object_id_and_dates(participant_feedback)
            print(" participant_feedback : ", participant_feedback)
            print()
        else:
            participant_feedback = {}
            print("participant_feedback  : ", participant_feedback)
            print()
    else:
        participant_feedback = {}
        print("  participant_feedback: ",participant_feedback )
        print()
    # Convert ObjectId and date fields to strings for JSON serialization
    convert_object_id_and_dates(performance_template)

    # Add employee and manager ratings to competencies
    for comp in performance_template.get('competencies', []):
        comp['employee_rating'] = None
        comp['manager_rating'] = None

    # Fetch the overall performance template (assuming a single document exists)
    overall_performance = overall_performance_collection.find_one({}, {'overall_summary_and_ratings': 1})

    if not overall_performance:
        return jsonify({"error": "No overall performance template found in P_overall_performance collection"}), 404

    # Convert ObjectId and date fields in overall_performance
    convert_object_id_and_dates(overall_performance)

    # Insert employee's goals, additional fields, and overall performance into my_performance_collection
    performance_data = {
        'person_name': employee_name,
        'performance_document_name': performance_document_name,
        'goals': goals_list,
        'description': performance_template.get('description'),
        'competencies': performance_template.get('competencies', []),
        'feedbacks': performance_template.get('feedbacks', []),
        'checkins': performance_template.get('check_ins', []),
        'participant_feedback': participant_feedback,  # Include fetched participant feedback
        'review_period': review_period,  # Include the review period in the performance document
        'overall_summary_and_ratings': overall_performance.get('overall_summary_and_ratings', {})
    }

    result = my_performance_collection.insert_one(performance_data)

    # Convert ObjectId to string for JSON serialization
    performance_data['_id'] = str(result.inserted_id)

    return jsonify({"message": "Goals and additional information added for employee successfully", "data": performance_data}), 201


# Update an existing goal
@my_performance_bp.route('/update_goal', methods=['POST'])
def update_goal():
    data = request.json
    employee_name = data.get('employee_name')
    goal_name = data.get('goal_name')
    updated_goal = data.get('updated_goal')

    if not employee_name or not goal_name or not updated_goal:
        return jsonify({"error": "Missing required parameters"}), 400

    result = my_performance_collection.update_one(
        {'employee_name': employee_name, 'goals.goal_name': goal_name},
        {'$set': {'goals.$': updated_goal}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify({"message": "Goal updated successfully"}), 200

# Delete a goal
@my_performance_bp.route('/delete_goal', methods=['POST'])
def delete_goal():
    data = request.json
    employee_name = data.get('employee_name')
    goal_name = data.get('goal_name')

    if not employee_name or not goal_name:
        return jsonify({"error": "Missing required parameters"}), 400

    result = my_performance_collection.update_one(
        {'employee_name': employee_name},
        {'$pull': {'goals': {'goal_name': goal_name}}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Goal not found or not deleted"}), 404

    return jsonify({"message": "Goal deleted successfully"}), 200
