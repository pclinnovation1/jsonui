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

# Function to get assignment details using employee unique ID (empsUniqID)
def get_assignment(empsUniqID):
    url = f"{ORACLE_HCM_BASE_URL}/emps/{empsUniqID}/child/assignments"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            return data["items"]  # Returning all assignments found
    return None

# Function to get job name using JobId with JobIdLOV API pattern
def get_job_name(job_id, job_lov_url):
    # Fit the JobId into the provided JobIdLOV URL
    url = f"{job_lov_url}?q=JobId={job_id}"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0].get("Name")  # Return the Job Name
    return None

# Function to get department name using DepartmentId
def get_department_name(department_id, department_lov_url):
    # Fit the DepartmentId into the provided DepartmentIdLOV URL
    url = f"{department_lov_url}?q=OrganizationId={department_id}"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0].get("Name")  # Return the Department Name
    return None

@app.route('/view_employee', methods=['POST'])
def view_employee_details():
    # Get the JSON data from the request
    data = request.json
    person_number = data.get('person_number')
    
    if not person_number:
        return jsonify({"error": "person_number is required"}), 400

    # Step 1: Get employee details based on person_number
    employee = get_employee(person_number)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    # Return the employee details as JSON response
    return jsonify(employee)

@app.route('/view_assignment', methods=['POST'])
def view_assignment_details():
    # Get the JSON data from the request
    data = request.json
    person_number = data.get('person_number')
    
    if not person_number:
        return jsonify({"error": "person_number is required"}), 400

    # Step 1: Get employee details based on person_number
    employee = get_employee(person_number)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    # Step 2: Get the unique ID of the employee
    empsUniqID = employee.get("links", [])[0].get("href").split('/')[-1] if employee.get("links") else None
    if not empsUniqID:
        return jsonify({"error": "Unique employee ID not found"}), 404
    
    # Step 3: Get assignment details based on the unique employee ID
    assignments = get_assignment(empsUniqID)
    if not assignments:
        return jsonify({"error": "No assignments found for this employee"}), 404

    # Step 4: For each assignment, fetch job name and department name
    for assignment in assignments:
        job_id = assignment.get("JobId")
        department_id = assignment.get("DepartmentId")
        
        # Extract the JobIdLOV and DepartmentIdLOV URLs from the 'links' in the assignment
        job_lov_link = next((link['href'] for link in assignment.get('links', []) if link.get('name') == 'JobIdLOV'), None)
        department_lov_link = next((link['href'] for link in assignment.get('links', []) if link.get('name') == 'DepartmentIdLOV'), None)
        
        if job_id and job_lov_link:
            job_name = get_job_name(job_id, job_lov_link)  # Fetch job name using JobIdLOV URL
            assignment["JobName"] = job_name if job_name else "Unknown Job"  # Add job name to the assignment details
        
        if department_id and department_lov_link:
            department_name = get_department_name(department_id, department_lov_link)  # Fetch department name using DepartmentIdLOV URL
            assignment["DepartmentName"] = department_name if department_name else "Unknown Department"  # Add department name to the assignment details

    # Return the assignment details including job names and department names as JSON response
    return jsonify(assignments)

if __name__ == '__main__':
    app.run(debug=True)
