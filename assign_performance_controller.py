# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config
# from bson import ObjectId

# # Define the Blueprint
# assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_document_collection = db['P_Performance_document']
# eligible_employee_collection = db['P_eligible_employee']
# assigned_performance_collection = db['P_assigned_performance']  # Collection to store assigned performance documents

# # Function to clone a performance document for an employee
# def clone_performance_document(employee_name, performance_document):
#     performance_document_copy = performance_document.copy()
#     performance_document_copy.pop('_id', None)  # Remove the original _id to create a new document
#     performance_document_copy['employee_name'] = employee_name
#     performance_document_copy['status'] = 'Assigned'
#     return performance_document_copy

# # API route to assign performance documents to eligible employees
# @assign_performance_bp.route('/assign_performance_documents', methods=['POST'])
# def assign_performance_documents():
#     data = request.json
#     performance_document_name = data.get('performance_document_name')

#     if not performance_document_name:
#         return jsonify({"error": "Missing required parameter: performance_document_name"}), 400

#     # Fetch the performance document template from P_Performance_document collection
#     performance_document = performance_document_collection.find_one({"performance_document_name": performance_document_name})

#     if not performance_document:
#         return jsonify({"error": f"No performance document found for name: {performance_document_name}"}), 404

#     # Fetch the eligible employees from P_eligible_employee collection
#     eligible_employee_entry = eligible_employee_collection.find_one({"performance_document_name": performance_document_name})

#     if not eligible_employee_entry:
#         return jsonify({"error": f"No eligible employees found for performance document: {performance_document_name}"}), 404

#     combined_employees = eligible_employee_entry.get('combined_employees', [])

#     # Assign the performance document to each eligible employee
#     assigned_documents = []
#     for employee_name in combined_employees:
#         employee_performance_document = clone_performance_document(employee_name, performance_document)
#         result = assigned_performance_collection.insert_one(employee_performance_document)
#         assigned_documents.append({"employee_name": employee_name, "assigned_document_id": str(result.inserted_id)})

#     return jsonify({"message": "Performance documents assigned successfully", "assigned_documents": assigned_documents}), 200















# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# # Define the Blueprint
# assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_document_collection = db['P_Performance_document']
# eligible_employee_collection = db['P_eligible_employee']
# assigned_performance_collection = db['P_assigned_performance']  # Collection to store assigned performance documents

# # Function to remove ratingScale from competencies
# def remove_rating_scale(competencies):
#     for comp in competencies:
#         if 'ratingScale' in comp:
#             del comp['ratingScale']
#     return competencies

# # Function to clone a performance document for an employee
# def clone_performance_document(employee_name, performance_document):
#     performance_document_copy = performance_document.copy()
#     performance_document_copy.pop('_id', None)  # Remove the original _id to create a new document
    
#     # Remove ratingScale from competencies
#     if 'competencies' in performance_document_copy:
#         performance_document_copy['competencies'] = remove_rating_scale(performance_document_copy['competencies'])
    
#     performance_document_copy['employee_name'] = employee_name
#     performance_document_copy['status'] = 'Assigned'
#     return performance_document_copy

# # API route to assign performance documents to eligible employees
# @assign_performance_bp.route('/assign_performance_documents', methods=['POST'])
# def assign_performance_documents():
#     data = request.json
#     performance_document_name = data.get('performance_document_name')

#     if not performance_document_name:
#         return jsonify({"error": "Missing required parameter: performance_document_name"}), 400

#     # Fetch the performance document template from P_Performance_document collection
#     performance_document = performance_document_collection.find_one({"performance_document_name": performance_document_name})

#     if not performance_document:
#         return jsonify({"error": f"No performance document found for name: {performance_document_name}"}), 404

#     # Fetch the eligible employees from P_eligible_employee collection
#     eligible_employee_entry = eligible_employee_collection.find_one({"performance_document_name": performance_document_name})

#     if not eligible_employee_entry:
#         return jsonify({"error": f"No eligible employees found for performance document: {performance_document_name}"}), 404

#     combined_employees = eligible_employee_entry.get('combined_employees', [])

#     # Assign the performance document to each eligible employee
#     assigned_documents = []
#     for employee_name in combined_employees:
#         employee_performance_document = clone_performance_document(employee_name, performance_document)
#         result = assigned_performance_collection.insert_one(employee_performance_document)
#         assigned_documents.append({"employee_name": employee_name, "assigned_document_id": str(result.inserted_id)})

#     return jsonify({"message": "Performance documents assigned successfully", "assigned_documents": assigned_documents}), 200

































































# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import config

# # Define the Blueprint
# assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# performance_document_collection = db['P_Performance_document']
# eligible_employee_collection = db['P_eligible_employee']
# assigned_performance_collection = db['P_assigned_performance']  # Collection to store assigned performance documents

# # Function to remove ratingScale from competencies
# def remove_rating_scale(competencies):
#     for comp in competencies:
#         if 'ratingScale' in comp:
#             del comp['ratingScale']
#     return competencies

# # Function to clone a performance document for an employee
# def clone_performance_document(employee_name, performance_document):
#     performance_document_copy = performance_document.copy()
#     performance_document_copy.pop('_id', None)  # Remove the original _id to create a new document
    
#     # Remove ratingScale from competencies
#     if 'competencies' in performance_document_copy:
#         performance_document_copy['competencies'] = remove_rating_scale(performance_document_copy['competencies'])
    
#     performance_document_copy['employee_name'] = employee_name
#     performance_document_copy['status'] = 'Assigned'
#     return performance_document_copy

# # API route to assign performance documents to eligible employees
# @assign_performance_bp.route('/assign_performance_documents', methods=['POST'])
# def assign_performance_documents():
#     data = request.json
#     performance_document_name = data.get('performance_document_name')

#     if not performance_document_name:
#         return jsonify({"error": "Missing required parameter: performance_document_name"}), 400

#     # Fetch the performance document template from P_Performance_document collection
#     performance_document = performance_document_collection.find_one({"performance_document_name": performance_document_name})

#     if not performance_document:
#         return jsonify({"error": f"No performance document found for name: {performance_document_name}"}), 404

#     # Fetch the eligible employees from P_eligible_employee collection
#     eligible_employee_entry = eligible_employee_collection.find_one({"performance_document_name": performance_document_name})

#     if not eligible_employee_entry:
#         return jsonify({"error": f"No eligible employees found for performance document: {performance_document_name}"}), 404

#     combined_employees = eligible_employee_entry.get('combined_employees', [])

#     # Assign the performance document to each eligible employee
#     assigned_documents = []
#     for employee_name in combined_employees:
#         employee_performance_document = clone_performance_document(employee_name, performance_document)
#         result = assigned_performance_collection.insert_one(employee_performance_document)
#         assigned_documents.append({"employee_name": employee_name, "assigned_document_id": str(result.inserted_id)})

#     return jsonify({"message": "Performance documents assigned successfully", "assigned_documents": assigned_documents}), 200



































from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

# Define the Blueprint
assign_performance_bp = Blueprint('assign_performance_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
performance_document_collection = db['P_Performance_document']
eligible_employee_collection = db['P_eligible_employee']
assigned_performance_collection = db['P_assigned_performance']  # Collection to store assigned performance documents

# Function to remove ratingScale from competencies
def remove_rating_scale(competencies):
    for comp in competencies:
        if 'ratingScale' in comp:
            del comp['ratingScale']
    return competencies

# Function to add feedback fields for employee and manager
def add_feedback_fields(feedbacks):
    if 'questions' in feedbacks:
        for question in feedbacks['questions']:
            question['employee_feedback'] = None
            question['manager_feedback'] = None
    return feedbacks

# Function to clone a performance document for an employee
def clone_performance_document(employee_name, performance_document):
    performance_document_copy = performance_document.copy()
    performance_document_copy.pop('_id', None)  # Remove the original _id to create a new document
    
    # Remove ratingScale from competencies
    if 'competencies' in performance_document_copy:
        performance_document_copy['competencies'] = remove_rating_scale(performance_document_copy['competencies'])

    # Add employee_feedback and manager_feedback to feedbacks
    if 'feedbacks' in performance_document_copy:
        performance_document_copy['feedbacks'] = add_feedback_fields(performance_document_copy['feedbacks'])
    
    performance_document_copy['employee_name'] = employee_name
    performance_document_copy['status'] = 'Assigned'
    return performance_document_copy

# API route to assign performance documents to eligible employees
@assign_performance_bp.route('/assign_performance_documents', methods=['POST'])
def assign_performance_documents():
    data = request.json
    performance_document_name = data.get('performance_document_name')

    if not performance_document_name:
        return jsonify({"error": "Missing required parameter: performance_document_name"}), 400

    # Fetch the performance document template from P_Performance_document collection
    performance_document = performance_document_collection.find_one({"performance_document_name": performance_document_name})

    if not performance_document:
        return jsonify({"error": f"No performance document found for name: {performance_document_name}"}), 404

    # Fetch the eligible employees from P_eligible_employee collection
    eligible_employee_entry = eligible_employee_collection.find_one({"performance_document_name": performance_document_name})

    if not eligible_employee_entry:
        return jsonify({"error": f"No eligible employees found for performance document: {performance_document_name}"}), 404

    combined_employees = eligible_employee_entry.get('combined_employees', [])

    # Assign the performance document to each eligible employee
    assigned_documents = []
    for employee_name in combined_employees:
        employee_performance_document = clone_performance_document(employee_name, performance_document)
        result = assigned_performance_collection.insert_one(employee_performance_document)
        assigned_documents.append({"employee_name": employee_name, "assigned_document_id": str(result.inserted_id)})

    return jsonify({"message": "Performance documents assigned successfully", "assigned_documents": assigned_documents}), 200
