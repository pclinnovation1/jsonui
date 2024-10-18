# from flask import Flask, request, jsonify
# import requests
# import json

# app = Flask(__name__)

# # Oracle Cloud HCM REST API base URL
# ORACLE_HCM_BASE_URL = 'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05'
# USERNAME = 'Vishal.Meena@payrollcloudcorp.com'
# PASSWORD = 'Welcome#12345'

# # Function to get employee details using person number
# def get_employee(person_number):
#     url = f"{ORACLE_HCM_BASE_URL}/emps?q=PersonNumber='{person_number}'"
#     response = requests.get(url, auth=(USERNAME, PASSWORD))
    
#     if response.status_code == 200:
#         data = response.json()
#         if data["items"]:
#             return data["items"][0]  # Returning the first item if found
#     return None

# # Function to get assignment details using the assignment URL
# def get_assignment_url(employee_data):
#     # Iterate through the links to find the "assignments" child URL
#     for link in employee_data.get('links', []):
#         if link['rel'] == 'child' and 'assignments' in link['href']:
#             return link['href']
#     return None

# # Function to fetch JobId based on Job Name
# def get_job_id(job_name):
#     url = f"{ORACLE_HCM_BASE_URL}/jobs?limit=500&onlyData=true&expand=all"
#     response = requests.get(url, auth=(USERNAME, PASSWORD))
    
#     if response.status_code == 200:
#         data = response.json()
#         for job in data.get('items', []):
#             if job.get('Name') == job_name:
#                 return job.get('JobId')
#     return None

# # Function to update assignment details using assignment ID
# def update_assignment(assignment_url, updated_data):
#     headers = {
#         'Content-Type': 'application/json'
#     }
    
#     # Make the PATCH request to update assignment
#     response = requests.patch(assignment_url, auth=(USERNAME, PASSWORD), headers=headers, data=json.dumps(updated_data))
    
#     if response.status_code in [200, 204]:
#         return {"message": "Assignment updated successfully"}
#     else:
#         return {"error": "Failed to update assignment", "details": response.text}

# @app.route('/update_assignment', methods=['POST'])
# def update_employee_assignment():
#     # Get data from the client request
#     data = request.json
#     person_number = data.get('person_number')
    
#     if not person_number:
#         return jsonify({"error": "Person number is required"}), 400
    
#     # Step 1: Get employee details based on person_number
#     employee = get_employee(person_number)
#     if not employee:
#         return jsonify({"error": "Employee not found"}), 404
    
#     # Step 2: Get the assignment URL from the employee details
#     assignment_url = get_assignment_url(employee)
#     if not assignment_url:
#         return jsonify({"error": "Assignment not found"}), 404
    
#     # Get the specific assignment URL
#     response = requests.get(assignment_url, auth=(USERNAME, PASSWORD))
#     if response.status_code != 200:
#         return jsonify({"error": "Failed to fetch assignment details", "details": response.text}), response.status_code
    
#     assignment_data = response.json()
#     if not assignment_data["items"]:
#         return jsonify({"error": "No assignment available for this employee"}), 404
    
#     # Get the first assignment's canonical URL for updating
#     assignment_details = assignment_data["items"][0]
#     update_url = None
#     for link in assignment_details.get('links', []):
#         if link['rel'] == 'canonical' and 'assignments' in link['href']:
#             update_url = link['href']
#             break
    
#     if not update_url:
#         return jsonify({"error": "Assignment update URL not found"}), 404

#     # Step 3: Fetch JobId if "JobName" is provided in the input
#     job_name = data.get('JobName')
#     if job_name:
#         job_id = get_job_id(job_name)
#         if not job_id:
#             return jsonify({"error": f"Job '{job_name}' not found"}), 404
#         data['JobId'] = job_id  # Replace the JobName with JobId in the payload
#         del data['JobName']  # Remove 'JobName' from the payload, as we are sending 'JobId'

#     # Remove 'person_number' from data as it is not part of the update payload
#     updated_data = {key: value for key, value in data.items() if key != 'person_number'}

#     # Step 4: Update the assignment details
#     result = update_assignment(update_url, updated_data)
    
#     return jsonify(result)

# if __name__ == '__main__':
#     app.run(debug=True)



































from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Oracle Cloud HCM REST API base URL
ORACLE_HCM_BASE_URL = 'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05'
USERNAME = 'Vishal.Meena@payrollcloudcorp.com'
PASSWORD = 'Welcome#12345'

# Function to get employee details using person number
def get_employee(person_number):
    url = f"{ORACLE_HCM_BASE_URL}/emps?q=PersonNumber='{person_number}'"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            return data["items"][0]  # Returning the first item if found
    return None

# Function to get assignment details using the assignment URL
def get_assignment_url(employee_data):
    for link in employee_data.get('links', []):
        if link['rel'] == 'child' and 'assignments' in link['href']:
            return link['href']
    return None

# Function to fetch JobId based on Job Name
def get_job_id(job_name):
    url = f"{ORACLE_HCM_BASE_URL}/jobs?limit=500&onlyData=true&expand=all"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        for job in data.get('items', []):
            if job.get('Name') == job_name:
                return job.get('JobId')
    return None

# Function to fetch OrganizationId based on Department Name
def get_department_id(department_name):
    url = f"{ORACLE_HCM_BASE_URL}/organizations?onlyData=true&limit=500"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        for org in data.get('items', []):
            if org.get('Name') == department_name:
                return org.get('OrganizationId')
    return None

# Function to update assignment details using assignment URL
def update_assignment(assignment_url, updated_data):
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.patch(assignment_url, auth=(USERNAME, PASSWORD), headers=headers, data=json.dumps(updated_data))
    
    if response.status_code in [200, 204]:
        return {"message": "Assignment updated successfully"}
    else:
        return {"error": "Failed to update assignment", "details": response.text}

@app.route('/update_assignment', methods=['POST'])
def update_employee_assignment():
    data = request.json
    person_number = data.get('person_number')

    if not person_number:
        return jsonify({"error": "Person number is required"}), 400
    
    employee = get_employee(person_number)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    assignment_url = get_assignment_url(employee)
    if not assignment_url:
        return jsonify({"error": "Assignment not found"}), 404
    
    response = requests.get(assignment_url, auth=(USERNAME, PASSWORD))
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch assignment details", "details": response.text}), response.status_code
    
    assignment_data = response.json()
    if not assignment_data["items"]:
        return jsonify({"error": "No assignment available for this employee"}), 404

    assignment_details = assignment_data["items"][0]
    update_url = None
    for link in assignment_details.get('links', []):
        if link['rel'] == 'canonical' and 'assignments' in link['href']:
            update_url = link['href']
            break
    
    if not update_url:
        return jsonify({"error": "Assignment update URL not found"}), 404

    job_name = data.get('JobName')
    if job_name:
        job_id = get_job_id(job_name)
        if not job_id:
            return jsonify({"error": f"Job '{job_name}' not found"}), 404
        data['JobId'] = job_id
        del data['JobName']

    department_name = data.get('DepartmentName')
    if department_name:
        department_id = get_department_id(department_name)
        if not department_id:
            return jsonify({"error": f"Department '{department_name}' not found"}), 404
        data['DepartmentId'] = department_id
        del data['DepartmentName']

    updated_data = {key: value for key, value in data.items() if key != 'person_number'}

    result = update_assignment(update_url, updated_data)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

