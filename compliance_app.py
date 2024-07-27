'''
from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1')
db = client['dev1']

# Function to fetch all data from collections
def fetch_data_from_collections():
    collection_names = ["HRM_employee_details", "LRN_course_assignment"]
    data = {}
    for collection_name in collection_names:
        collection = db[collection_name]
        data[collection_name] = list(collection.find())
    return data

def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

# Function to check compliance status
def check_compliance(hrm_data, lrn_data, assignment_type_filter):
    compliance_status = []

    # Create a dictionary for HRM data keyed by person_name
    hrm_dict = {doc['person_name']: doc for doc in hrm_data}

    for lrn_doc in lrn_data:
        if lrn_doc.get('assignment_type') == assignment_type_filter:
            
            person_name = lrn_doc.get('person_name')
            hrm_doc = hrm_dict.get(person_name)

            if hrm_doc:
                completion_date_str = lrn_doc.get('completion_date')
                due_date_str = lrn_doc.get('due_date')
                course_name = lrn_doc.get('course_name')
                department = hrm_doc.get('department', 'N/A')

                completion_date = parse_date(completion_date_str) if completion_date_str else None
                due_date = parse_date(due_date_str) if due_date_str else None

                if completion_date and due_date:
                    status = "Compliant" if completion_date <= due_date else "Non-Compliant"
                else:
                    status = "Data Missing"

                compliance_status.append({
                    'person_name': person_name,
                    'course_name': course_name,
                    'due_date': due_date_str,
                    'completion_date': completion_date_str,
                    'department': department,
                    'compliant_status': status
                })

        return compliance_status

# POST route to deliver compliance status
@app.route('/compliance-status', methods=['POST'])
def compliance_status():
    request_data = request.json
    assignment_type_filter = request_data.get('assignment_type')

    data = fetch_data_from_collections()
    hrm_data = data.get('HRM_employee_details', [])
    lrn_data = data.get('LRN_course_assignment', [])
    compliance_status = check_compliance(hrm_data, lrn_data, assignment_type_filter)
    return jsonify(compliance_status), 200

if __name__ == '__main__':
    app.run(debug=True)
'''

from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1')
db = client['dev1']

# Function to fetch all data from collections
def fetch_data_from_collections():
    collection_names = ["HRM_employee_details", "LRN_course_assignment"]
    data = {}
    for collection_name in collection_names:
        collection = db[collection_name]
        data[collection_name] = list(collection.find())
    return data

def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

# Function to check compliance status
def check_compliance(hrm_data, lrn_data, assignment_type):
    compliance_status = []

    # Create a dictionary for HRM data keyed by person_name
    hrm_dict = {doc['person_name']: doc for doc in hrm_data}

    for lrn_doc in lrn_data:
        if assignment_type and lrn_doc.get('assignment_type') != assignment_type:
            continue

        person_name = lrn_doc.get('person_name')
        hrm_doc = hrm_dict.get(person_name)

        if hrm_doc:
            completion_date_str = lrn_doc.get('completion_date')
            due_date_str = lrn_doc.get('due_date')
            course_name = lrn_doc.get('course_name')
            department = hrm_doc.get('department', 'N/A')

            completion_date = parse_date(completion_date_str) if completion_date_str else None
            due_date = parse_date(due_date_str) if due_date_str else None

            if completion_date and due_date:
                status = "Compliant" if completion_date <= due_date else "Non-Compliant"
            else:
                status = "Data Missing"

            compliance_status.append({
                'person_name': person_name,
                'course_name': course_name,
                'due_date': due_date_str,
                'completion_date': completion_date_str,
                'department': department,
                'compliant_status': status
            })

    return compliance_status

# POST route to deliver compliance status
@app.route('/compliance-status', methods=['POST'])
def compliance_status():
    request_data = request.json
    assignment_type = request_data.get('assignment_type') if request_data else None

    data = fetch_data_from_collections()
    hrm_data = data.get('HRM_employee_details', [])
    lrn_data = data.get('LRN_course_assignment', [])
    compliance_status = check_compliance(hrm_data, lrn_data, assignment_type)
    return jsonify(compliance_status), 200

if __name__ == '__main__':
    app.run(debug=True)



