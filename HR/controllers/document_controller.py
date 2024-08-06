from flask import request, jsonify, send_file, Blueprint
from pymongo import MongoClient
import gridfs
import config
from datetime import datetime



# Initialize MongoDB client and database
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
fs = gridfs.GridFS(db)

# Define the Employee model
class Employee:
    def __init__(self, db):
        self.collection = db['OD_oras_employee_details']
        self.document_collection = db.documents
        self.fs = gridfs.GridFS(db)

    def get_employee(self, person_name):
        return self.collection.find_one({"person_name": person_name})

    def update_employee(self, person_name, update_data):
        return self.collection.update_one({"person_name": person_name}, {"$set": update_data})

    def delete_employee(self, person_name):
        return self.collection.delete_one({"person_name": person_name})

    def save_file(self, file, filename):
        self.fs.put(file, filename=filename)
        return filename

    def get_file(self, filename):
        return self.fs.find_one({"filename": filename})

    def delete_file(self, filename):
        file = self.fs.find_one({"filename": filename})
        if file:
            self.fs.delete(file._id)

    def add_document(self, document_data):
        return self.document_collection.insert_one(document_data).inserted_id

    def get_document(self, person_name, filename):
        return self.document_collection.find_one({"person_name": person_name, "filename": filename})

    def delete_document(self, person_name, filename):
        return self.document_collection.delete_one({"person_name": person_name, "filename": filename})

employee_model = Employee(db)

document_blueprint = Blueprint('document', __name__)

@document_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    person_name = request.form.get('person_name')
    if not person_name:
        return jsonify({"error": "Person name is required"}), 400

    employee = employee_model.get_employee(person_name)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    filename = file.filename
    employee_model.save_file(file, filename)
    
    if 'files' in employee:
        employee['files'].append(filename)
    else:
        employee['files'] = [filename]
    employee_model.update_employee(person_name, {"files": employee['files']})
    
    # Add document to the documents collection
    uploaded_at = request.form.get('uploaded_at')
    if not uploaded_at:
        uploaded_at = datetime.utcnow()
    document_data = {
        "person_name": person_name,
        "filename": filename,
        "uploaded_at": uploaded_at
    }
    employee_model.add_document(document_data)
    
    return jsonify({"message": "File successfully uploaded", "filename": filename}), 201

@document_blueprint.route('/get_employee', methods=['POST'])
def get_employee():
    person_name = request.json.get('person_name')
    if not person_name:
        return jsonify({"error": "Person name is required"}), 400
    employee = employee_model.get_employee(person_name)
    if employee:
        return jsonify({
            "person_name": employee['person_name'],
            "files": employee.get('files', [])
        }), 200
    else:
        return jsonify({"error": "Employee not found"}), 404

@document_blueprint.route('/get_employee_file', methods=['POST'])
def get_employee_file():
    data = request.json
    person_name = data.get('person_name')
    filename = data.get('filename')
    if not person_name or not filename:
        return jsonify({"error": "Person name and filename are required"}), 400
    employee = employee_model.get_employee(person_name)
    if employee and 'files' in employee and filename in employee['files']:
        file = employee_model.get_file(filename)
        if file:
            return send_file(file, download_name=file.filename, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    else:
        return jsonify({"error": "Employee or file not found"}), 404

@document_blueprint.route('/delete_employee_file', methods=['POST'])
def delete_employee_file():
    data = request.json
    person_name = data.get('person_name')
    filename = data.get('filename')
    if not person_name or not filename:
        return jsonify({"error": "Person name and filename are required"}), 400
    employee = employee_model.get_employee(person_name)
    if employee and 'files' in employee and filename in employee['files']:
        # Remove the file from GridFS
        employee_model.delete_file(filename)
        # Update the employee's file list
        employee['files'].remove(filename)
        employee_model.update_employee(person_name, {"files": employee['files']})
        # Remove the document from the documents collection
        employee_model.delete_document(person_name, filename)
        return jsonify({"message": "File successfully deleted"}), 200
    else:
        return jsonify({"error": "Employee or file not found"}), 404

@document_blueprint.route('/delete_employee', methods=['POST'])
def delete_employee():
    data = request.json
    person_name = data.get('person_name')
    if not person_name:
        return jsonify({"error": "Person name is required"}), 400
    print(f"Attempting to delete employee: {person_name}")  # Debug statement
    employee = employee_model.get_employee(person_name)
    if employee:
        print(f"Employee found: {employee}")  # Debug statement
        # Delete associated files
        if 'files' in employee:
            for filename in employee['files']:
                print(f"Deleting file: {filename}")  # Debug statement
                employee_model.delete_file(filename)
                # Remove the document from the documents collection
                employee_model.delete_document(person_name, filename)
        result = employee_model.delete_employee(person_name)
        if result.deleted_count > 0:
            print(f"Employee {person_name} deleted successfully")  # Debug statement
            return jsonify({"message": "Employee and associated files deleted successfully"}), 200
        else:
            print(f"Failed to delete employee {person_name}")  # Debug statement
            return jsonify({"error": "Failed to delete employee"}), 500
    else:
        print(f"Employee {person_name} not found")  # Debug statement
        return jsonify({"error": "Employee not found"}), 404

