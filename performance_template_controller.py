


# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# performance_template_bp = Blueprint('performance_template_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]

# # Helper function to convert keys to lowercase and replace spaces with underscores
# def lowercase_keys(data):
#     if isinstance(data, dict):
#         return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [lowercase_keys(item) for item in data]
#     else:
#         return data

# @performance_template_bp.route('/create', methods=['POST'])
# def create_template():
#     try:
#         data = request.get_json()
#         if not data:
#             raise ValueError("No JSON payload found")

#         data = lowercase_keys(data)

#         performance_template_collection.insert_one(data)
#         return jsonify({'message': 'Template created successfully'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/get', methods=['POST'])
# def get_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
#         template = performance_template_collection.find_one({"general.name": template_name})
        
#         if template:
#             template['_id'] = str(template['_id'])
#             return jsonify(template), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/update', methods=['POST'])
# def update_template():
#     try:
#         data = request.get_json()
#         data = lowercase_keys(data)
#         template_name = data.get('general', {}).get('name')
        
#         result = performance_template_collection.update_one({"general.name": template_name}, {"$set": data})
#         if result.matched_count > 0:
#             return jsonify({"message": "Template updated successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/delete', methods=['POST'])
# def delete_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
        
#         result = performance_template_collection.delete_one({"general.name": template_name})
#         if result.deleted_count > 0:
#             return jsonify({"message": "Template deleted successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400



















# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# performance_template_bp = Blueprint('performance_template_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# competency_collection = db[config.COMPETENCY_COLLECTION_NAME]
# feedback_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
# check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]

# # Helper function to convert keys to lowercase and replace spaces with underscores
# def lowercase_keys(data):
#     if isinstance(data, dict):
#         return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [lowercase_keys(item) for item in data]
#     else:
#         return data

# def fetch_details(names, collection):
#     if isinstance(names, list):
#         return list(collection.find({"name": {"$in": names}}))
#     else:
#         return collection.find_one({"name": names})

# @performance_template_bp.route('/create', methods=['POST'])
# def create_template():
#     try:
#         data = request.get_json()
#         if not data:
#             raise ValueError("No JSON payload found")

#         data = lowercase_keys(data)

#         competency_names = data.get('competencies', [])
#         feedback_names = data.get('feedbacks', [])
#         check_in_names = data.get('check_ins', [])

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]

#         performance_template_collection.insert_one(data)
#         return jsonify({'message': 'Template created successfully'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/get', methods=['POST'])
# def get_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
#         template = performance_template_collection.find_one({"general.name": template_name})
        
#         if template:
#             template['_id'] = str(template['_id'])
#             return jsonify(template), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/update', methods=['POST'])
# def update_template():
#     try:
#         data = request.get_json()
#         data = lowercase_keys(data)
#         template_name = data.get('general', {}).get('name')
        
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]

#         result = performance_template_collection.update_one({"general.name": template_name}, {"$set": data})
#         if result.matched_count > 0:
#             return jsonify({"message": "Template updated successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/delete', methods=['POST'])
# def delete_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
        
#         result = performance_template_collection.delete_one({"general.name": template_name})
#         if result.deleted_count > 0:
#             return jsonify({"message": "Template deleted successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/fetch-details', methods=['POST'])
# def fetch_template_details():
#     try:
#         data = request.get_json()
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
        
#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
        
#         response = {
#             "competencies": competencies if isinstance(competencies, list) else [competencies],
#             "feedbacks": feedbacks if isinstance(feedbacks, list) else [feedbacks],
#             "check_ins": check_ins if isinstance(check_ins, list) else [check_ins]
#         }
        
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400




































































# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# performance_template_bp = Blueprint('performance_template_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# competency_collection = db[config.COMPETENCY_COLLECTION_NAME]
# feedback_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
# check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]
# role_collection = db[config.PERFORMANCE_ROLE_COLLECTION_NAME]
# document_type_collection = db[config.PERFORMANCE_DOCUMENT_TYPE_COLLECTION_NAME]
# participant_feedback_template_collection = db["P_ParticipantFeedbackTemplate"]


# # Helper function to convert keys to lowercase and replace spaces with underscores
# def lowercase_keys(data):
#     if isinstance(data, dict):
#         return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [lowercase_keys(item) for item in data]
#     else:
#         return data

# def fetch_details(names, collection):
#     if isinstance(names, list):
#         return list(collection.find({"name": {"$in": names}}))
#     else:
#         return collection.find_one({"name": names})



# @performance_template_bp.route('/create', methods=['POST'])
# def create_template():
#     try:
#         data = request.get_json()
#         if not data:
#             raise ValueError("No JSON payload found")

#         data = lowercase_keys(data)

#         # Fetch related data from other collections
#         competency_names = data.get('competencies', [])
#         feedback_names = data.get('feedbacks', [])
#         check_in_names = data.get('check_ins', [])
#         role_names = data.get('roles', [])
#         document_type_name = data.get('performance_document_type', {}).get('name', '')
#         participant_feedback_template_name = data.get('participant_feedback', {}).get('template_name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         roles = fetch_details(role_names, role_collection)
#         document_type = fetch_details(document_type_name, document_type_collection)
#         participant_feedback_template = fetch_details(participant_feedback_template_name, participant_feedback_template_collection)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['roles'] = roles if isinstance(roles, list) else [roles]
#         data['performance_document_type'] = document_type
#         data['participant_feedback_template'] = participant_feedback_template

#         # Add Task List (if provided)
#         data['tasks'] = data.get('tasks', [])

#         performance_template_collection.insert_one(data)
#         return jsonify({'message': 'Template created successfully', 'data': data}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400


# @performance_template_bp.route('/get', methods=['POST'])
# def get_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
#         template = performance_template_collection.find_one({"general.name": template_name})
        
#         if template:
#             template['_id'] = str(template['_id'])
#             return jsonify(template), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/update', methods=['POST'])
# def update_template():
#     try:
#         data = request.get_json()
#         data = lowercase_keys(data)
#         template_name = data.get('general', {}).get('name')
        
#         # Fetch related data from other collections
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
#         role_names = data.get('roles', [])
#         document_type_name = data.get('performance_document_type', {}).get('name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         roles = fetch_details(role_names, role_collection)
#         document_type = fetch_details(document_type_name, document_type_collection)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['roles'] = roles if isinstance(roles, list) else [roles]
#         data['performance_document_type'] = document_type

#         # Add Task List (if provided)
#         data['tasks'] = data.get('tasks', [])

#         result = performance_template_collection.update_one({"general.name": template_name}, {"$set": data})
#         if result.matched_count > 0:
#             return jsonify({"message": "Template updated successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/delete', methods=['POST'])
# def delete_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
        
#         result = performance_template_collection.delete_one({"general.name": template_name})
#         if result.deleted_count > 0:
#             return jsonify({"message": "Template deleted successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/fetch-details', methods=['POST'])
# def fetch_template_details():
#     try:
#         data = request.get_json()
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
#         role_names = data.get('roles', [])
#         document_type_name = data.get('performance_document_type', {}).get('name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         roles = fetch_details(role_names, role_collection)
#         document_type = fetch_details(document_type_name, document_type_collection)
        
#         response = {
#             "competencies": competencies if isinstance(competencies, list) else [competencies],
#             "feedbacks": feedbacks if isinstance(feedbacks, list) else [feedbacks],
#             "check_ins": check_ins if isinstance(check_ins, list) else [check_ins],
#             "roles": roles if isinstance(roles, list) else [roles],
#             "performance_document_type": document_type
#         }
        
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400
































# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# from bson import ObjectId
# import config

# performance_template_bp = Blueprint('performance_template_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# competency_collection = db[config.COMPETENCY_COLLECTION_NAME]
# feedback_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
# check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]
# role_collection = db[config.PERFORMANCE_ROLE_COLLECTION_NAME]
# document_type_collection = db[config.PERFORMANCE_DOCUMENT_TYPE_COLLECTION_NAME]
# participant_feedback_template_collection = db["P_ParticipantFeedbackTemplate"]

# # Helper function to convert keys to lowercase and replace spaces with underscores
# def lowercase_keys(data):
#     if isinstance(data, dict):
#         return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [lowercase_keys(item) for item in data]
#     else:
#         return data

# # Helper function to convert ObjectId to string
# def convert_object_id(data):
#     if isinstance(data, list):
#         return [convert_object_id(item) for item in data]
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if isinstance(value, ObjectId):
#                 data[key] = str(value)
#             elif isinstance(value, (dict, list)):
#                 data[key] = convert_object_id(value)
#     return data

# def fetch_details(names, collection):
#     if isinstance(names, list):
#         return list(collection.find({"name": {"$in": names}}))
#     else:
#         return collection.find_one({"name": names})

# # @performance_template_bp.route('/create', methods=['POST'])
# # def create_template():
# #     try:
# #         data = request.get_json()
# #         if not data:
# #             raise ValueError("No JSON payload found")

# #         data = lowercase_keys(data)

# #         # Fetch related data from other collections
# #         competency_names = data.get('competencies', [])
# #         feedback_names = data.get('feedbacks', [])
# #         check_in_names = data.get('check_ins', [])
# #         role_names = data.get('roles', [])
# #         document_type_name = data.get('performance_document_type', {}).get('name', '')
# #         participant_feedback_template_name = data.get('participant_feedback', {}).get('template_name', '')

# #         competencies = fetch_details(competency_names, competency_collection)
# #         feedbacks = fetch_details(feedback_names, feedback_collection)
# #         check_ins = fetch_details(check_in_names, check_in_collection)
# #         roles = fetch_details(role_names, role_collection)
# #         document_type = fetch_details(document_type_name, document_type_collection)
# #         participant_feedback_template = fetch_details(participant_feedback_template_name, participant_feedback_template_collection)

# #         # Convert ObjectId fields to strings
# #         competencies = convert_object_id(competencies)
# #         feedbacks = convert_object_id(feedbacks)
# #         check_ins = convert_object_id(check_ins)
# #         roles = convert_object_id(roles)
# #         document_type = convert_object_id(document_type)
# #         participant_feedback_template = convert_object_id(participant_feedback_template)

# #         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
# #         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
# #         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
# #         data['roles'] = roles if isinstance(roles, list) else [roles]
# #         data['performance_document_type'] = document_type
# #         data['participant_feedback_template'] = participant_feedback_template

# #         # Add Task List (if provided)
# #         data['tasks'] = data.get('tasks', [])

# #         performance_template_collection.insert_one(data)
# #         return jsonify({'message': 'Template created successfully', 'data': data}), 201
# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 400


# @performance_template_bp.route('/create', methods=['POST'])
# def create_template():
#     try:
#         data = request.get_json()
#         if not data:
#             raise ValueError("No JSON payload found")
        
#         print("Initial Data:", data)  # Debugging statement

#         data = lowercase_keys(data)

#         # Fetch related data from other collections
#         competency_names = data.get('competencies', [])
#         feedback_names = data.get('feedbacks', [])
#         check_in_names = data.get('check_ins', [])
#         role_names = data.get('roles', [])
#         document_type_name = data.get('performance_document_type', {}).get('name', '')
#         participant_feedback_template_name = data.get('participant_feedback', {}).get('template_name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         roles = fetch_details(role_names, role_collection)
#         document_type = fetch_details(document_type_name, document_type_collection)
#         participant_feedback_template = fetch_details(participant_feedback_template_name, participant_feedback_template_collection)

#         print("Fetched Competencies:", competencies)  # Debugging statement
#         print("Fetched Feedbacks:", feedbacks)  # Debugging statement
#         print("Fetched Check-ins:", check_ins)  # Debugging statement
#         print("Fetched Roles:", roles)  # Debugging statement
#         print("Fetched Document Type:", document_type)  # Debugging statement
#         print("Fetched Participant Feedback Template:", participant_feedback_template)  # Debugging statement

#         # Convert ObjectId fields to strings
#         competencies = convert_object_id(competencies)
#         feedbacks = convert_object_id(feedbacks)
#         check_ins = convert_object_id(check_ins)
#         roles = convert_object_id(roles)
#         document_type = convert_object_id(document_type)
#         participant_feedback_template = convert_object_id(participant_feedback_template)

#         print("Converted Competencies:", competencies)  # Debugging statement
#         print("Converted Feedbacks:", feedbacks)  # Debugging statement
#         print("Converted Check-ins:", check_ins)  # Debugging statement
#         print("Converted Roles:", roles)  # Debugging statement
#         print("Converted Document Type:", document_type)  # Debugging statement
#         print("Converted Participant Feedback Template:", participant_feedback_template)  # Debugging statement

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['roles'] = roles if isinstance(roles, list) else [roles]
#         data['performance_document_type'] = document_type
#         data['participant_feedback_template'] = participant_feedback_template

#         # Add Task List (if provided)
#         data['tasks'] = data.get('tasks', [])

#         print("Final Data to Insert:", data)  # Debugging statement

#         performance_template_collection.insert_one(data)
#         return jsonify({'message': 'Template created successfully', 'data': data}), 201
#     except Exception as e:
#         print("Error occurred:", str(e))  # Debugging statement
#         return jsonify({'error': str(e)}), 400





# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# from bson import ObjectId
# from datetime import datetime
# import config

# performance_template_bp = Blueprint('performance_template_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# competency_collection = db[config.COMPETENCY_COLLECTION_NAME]
# feedback_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
# check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]
# participant_feedback_template_collection = db["P_ParticipantFeedbackTemplate"]

# # Helper function to convert keys to lowercase and replace spaces with underscores
# def lowercase_keys(data):
#     if isinstance(data, dict):
#         return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [lowercase_keys(item) for item in data]
#     else:
#         return data

# # Helper function to convert ObjectId and datetime fields to strings
# def convert_object_id(data):
#     if isinstance(data, list):
#         return [convert_object_id(item) for item in data]
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if isinstance(value, ObjectId):
#                 data[key] = str(value)
#             elif isinstance(value, datetime):
#                 data[key] = value.isoformat()  # Convert datetime to ISO 8601 string
#             elif isinstance(value, (dict, list)):
#                 data[key] = convert_object_id(value)
#     return data

# def fetch_details(name, collection):
#     return collection.find_one({"name": name})

# @performance_template_bp.route('/create', methods=['POST'])
# def create_template():
#     try:
#         data = request.get_json()
#         if not data:
#             raise ValueError("No JSON payload found")

#         print("Initial Data:", data)  # Debugging statement

#         data = lowercase_keys(data)

#         # Fetch related data from other collections
#         competency_names = data.get('competencies', [])
#         feedback_names = data.get('feedbacks', [])
#         check_in_names = data.get('check_ins', [])
#         participant_feedback_template_name = data.get('participant_feedback', {}).get('template_name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         participant_feedback_template = fetch_details(participant_feedback_template_name, participant_feedback_template_collection)

#         print("Fetched Competencies:", competencies)  # Debugging statement
#         print("Fetched Feedbacks:", feedbacks)  # Debugging statement
#         print("Fetched Check-ins:", check_ins)  # Debugging statement
#         print("Fetched Participant Feedback Template:", participant_feedback_template)  # Debugging statement

#         # Convert ObjectId and datetime fields to strings
#         competencies = convert_object_id(competencies)
#         feedbacks = convert_object_id(feedbacks)
#         check_ins = convert_object_id(check_ins)
#         participant_feedback_template = convert_object_id(participant_feedback_template)

#         print("Converted Competencies:", competencies)  # Debugging statement
#         print("Converted Feedbacks:", feedbacks)  # Debugging statement
#         print("Converted Check-ins:", check_ins)  # Debugging statement
#         print("Converted Participant Feedback Template:", participant_feedback_template)  # Debugging statement

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['participant_feedback_template'] = participant_feedback_template

#         # Add Task List (if provided)
#         data['tasks'] = data.get('tasks', [])

#         # Final check to convert any remaining ObjectIds or datetimes
#         data = convert_object_id(data)

#         print("Final Data to Insert:", data)  # Debugging statement

#         performance_template_collection.insert_one(data)
#         return jsonify({'message': 'Template created successfully', 'data': data}), 201
#     except Exception as e:
#         print("Error occurred:", str(e))  # Debugging statement
#         return jsonify({'error': str(e)}), 400


# @performance_template_bp.route('/get', methods=['POST'])
# def get_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
#         template = performance_template_collection.find_one({"general.name": template_name})
        
#         if template:
#             template = convert_object_id(template)  # Convert ObjectId to string
#             return jsonify(template), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/update', methods=['POST'])
# def update_template():
#     try:
#         data = request.get_json()
#         data = lowercase_keys(data)
#         template_name = data.get('general', {}).get('name')
        
#         # Fetch related data from other collections
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
#         role_names = data.get('roles', [])
#         document_type_name = data.get('performance_document_type', {}).get('name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         # roles = fetch_details(role_names, role_collection)
#         # document_type = fetch_details(document_type_name, document_type_collection)

#         # Convert ObjectId fields to strings
#         competencies = convert_object_id(competencies)
#         feedbacks = convert_object_id(feedbacks)
#         check_ins = convert_object_id(check_ins)
#         roles = convert_object_id(roles)
#         document_type = convert_object_id(document_type)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['roles'] = roles if isinstance(roles, list) else [roles]
#         data['performance_document_type'] = document_type

#         # Add Task List (if provided)
#         data['tasks'] = data.get('tasks', [])

#         result = performance_template_collection.update_one({"general.name": template_name}, {"$set": data})
#         if result.matched_count > 0:
#             return jsonify({"message": "Template updated successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/delete', methods=['POST'])
# def delete_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
        
#         result = performance_template_collection.delete_one({"general.name": template_name})
#         if result.deleted_count > 0:
#             return jsonify({"message": "Template deleted successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/fetch-details', methods=['POST'])
# def fetch_template_details():
#     try:
#         data = request.get_json()
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
#         role_names = data.get('roles', [])
#         document_type_name = data.get('performance_document_type', {}).get('name', '')

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         # roles = fetch_details(role_names, role_collection)
#         # document_type = fetch_details(document_type_name, document_type_collection)

#         # Convert ObjectId fields to strings
#         competencies = convert_object_id(competencies)
#         feedbacks = convert_object_id(feedbacks)
#         check_ins = convert_object_id(check_ins)
#         roles = convert_object_id(roles)
#         document_type = convert_object_id(document_type)

#         response = {
#             "competencies": competencies if isinstance(competencies, list) else [competencies],
#             "feedbacks": feedbacks if isinstance(feedbacks, list) else [feedbacks],
#             "check_ins": check_ins if isinstance(check_ins, list) else [check_ins],
#             "roles": roles if isinstance(roles, list) else [roles],
#             "performance_document_type": document_type
#         }
        
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400





























# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# performance_template_bp = Blueprint('performance_template_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_template_collection = db[config.PERFORMANCE_TEMPLATE_COLLECTION_NAME]
# competency_collection = db[config.COMPETENCY_COLLECTION_NAME]
# feedback_collection = db[config.FEEDBACK_TEMPLATE_COLLECTION_NAME]
# check_in_collection = db[config.CHECK_IN_TEMPLATE_COLLECTION_NAME]
# participant_feedback_collection = db['P_ParticipantFeedbackTemplate']  # New collection

# # Helper function to convert keys to lowercase and replace spaces with underscores
# def lowercase_keys(data):
#     if isinstance(data, dict):
#         return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [lowercase_keys(item) for item in data]
#     else:
#         return data

# def fetch_details(names, collection):
#     if isinstance(names, list):
#         return list(collection.find({"name": {"$in": names}}))
#     else:
#         return collection.find_one({"name": names})

# @performance_template_bp.route('/create', methods=['POST'])
# def create_template():
#     try:
#         data = request.get_json()
#         if not data:
#             raise ValueError("No JSON payload found")

#         data = lowercase_keys(data)
#         print("data: ", data)
#         print()

#         template_name = data.get('general', {}).get('name')
#         print("template_name: ", template_name)
#         print()

#         competency_names = data.get('competencies', [])
#         feedback_names = data.get('feedbacks', [])
#         check_in_names = data.get('check_ins', [])
#         participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
#         print("participant_feedback_name: ", participant_feedback_name)
#         print()

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection)
#         print("participant_feedback:  ", participant_feedback)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['participant_feedback'] = participant_feedback

#         performance_template_collection.insert_one(data)
#         return jsonify({'message': 'Template created successfully'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/get', methods=['POST'])
# def get_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
#         template = performance_template_collection.find_one({"general.name": template_name})
        
#         if template:
#             template['_id'] = str(template['_id'])
#             return jsonify(template), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/update', methods=['POST'])
# def update_template():
#     try:
#         data = request.get_json()
#         data = lowercase_keys(data)

#         # print("data: ", data)
#         # print()

#         template_name = data.get('general', {}).get('name')
#         # print("template_name: ", template_name)
#         # print()
        
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
#         participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
#         # print("participant_feedback_name: ", participant_feedback_name)

#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection)

#         data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
#         data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
#         data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
#         data['participant_feedback'] = participant_feedback

#         result = performance_template_collection.update_one({"general.name": template_name}, {"$set": data})
#         if result.matched_count > 0:
#             return jsonify({"message": "Template updated successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/delete', methods=['POST'])
# def delete_template():
#     try:
#         data = request.get_json()
#         template_name = data.get('general', {}).get('name')
        
#         result = performance_template_collection.delete_one({"general.name": template_name})
#         if result.deleted_count > 0:
#             return jsonify({"message": "Template deleted successfully"}), 200
#         else:
#             return jsonify({"message": "Template not found"}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @performance_template_bp.route('/fetch-details', methods=['POST'])
# def fetch_template_details():
#     try:
#         data = request.get_json()
#         competency_names = data.get('competency_name', [])
#         feedback_names = data.get('feedback_name', [])
#         check_in_names = data.get('check_in_name', [])
#         participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
        
#         competencies = fetch_details(competency_names, competency_collection)
#         feedbacks = fetch_details(feedback_names, feedback_collection)
#         check_ins = fetch_details(check_in_names, check_in_collection)
#         participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection)
        
#         response = {
#             "competencies": competencies if isinstance(competencies, list) else [competencies],
#             "feedbacks": feedbacks if isinstance(feedbacks, list) else [feedbacks],
#             "check_ins": check_ins if isinstance(check_ins, list) else [check_ins],
#             "participant_feedback": participant_feedback
#         }
        
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400










































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
participant_feedback_collection = db['P_ParticipantFeedbackTemplate']  # Participant feedback collection

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
        feedback_names = data.get('feedbacks', [])
        check_in_names = data.get('check_ins', [])
        participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
        
        competencies = fetch_details(competency_names, competency_collection)
        feedbacks = fetch_details(feedback_names, feedback_collection)
        check_ins = fetch_details(check_in_names, check_in_collection)
        participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name")

        data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
        data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
        data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
        data['participant_feedback'] = participant_feedback

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

        template_name = data.get('general', {}).get('name')
        
        competency_names = data.get('competency_name', [])
        feedback_names = data.get('feedback_name', [])
        check_in_names = data.get('check_in_name', [])
        participant_feedback_name = data.get('participant_feedback', {}).get('template_name')

        competencies = fetch_details(competency_names, competency_collection)
        feedbacks = fetch_details(feedback_names, feedback_collection)
        check_ins = fetch_details(check_in_names, check_in_collection)
        participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name")

        data['competencies'] = competencies if isinstance(competencies, list) else [competencies]
        data['feedbacks'] = feedbacks if isinstance(feedbacks, list) else [feedbacks]
        data['check_ins'] = check_ins if isinstance(check_ins, list) else [check_ins]
        data['participant_feedback'] = participant_feedback

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

@performance_template_bp.route('/fetch-details', methods=['POST'])
def fetch_template_details():
    try:
        data = request.get_json()
        competency_names = data.get('competency_name', [])
        feedback_names = data.get('feedback_name', [])
        check_in_names = data.get('check_in_name', [])
        participant_feedback_name = data.get('participant_feedback', {}).get('template_name')
        
        competencies = fetch_details(competency_names, competency_collection)
        feedbacks = fetch_details(feedback_names, feedback_collection)
        check_ins = fetch_details(check_in_names, check_in_collection)
        participant_feedback = fetch_details(participant_feedback_name, participant_feedback_collection, query_field="template_name")
        
        response = {
            "competencies": competencies if isinstance(competencies, list) else [competencies],
            "feedbacks": feedbacks if isinstance(feedbacks, list) else [feedbacks],
            "check_ins": check_ins if isinstance(check_ins, list) else [check_ins],
            "participant_feedback": participant_feedback
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
