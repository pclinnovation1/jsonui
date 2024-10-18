from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Oracle Cloud HCM REST API base URL and credentials
ORACLE_HCM_BASE_URL = 'https://iaihgs-dev1.fa.ocs.oraclecloud.com/hcmRestApi/resources/11.13.18.05'
USERNAME = 'Vishal.Meena@payrollcloudcorp.com'  # Replace with your actual username
PASSWORD = 'Welcome#12345'  # Replace with your actual password

# Function to get empsUniqID using the person number
def get_employee_unique_id(person_number):
    # API URL to fetch employee data using person number
    api_url = f"{ORACLE_HCM_BASE_URL}/emps?q=PersonNumber='{person_number}'&expand=all&limit=1"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the GET request to Oracle Cloud API
    response = requests.get(api_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    # Check the response status
    if response.status_code == 200:
        data = response.json()
        if data.get("items"):
            # Extract the empsUniqID from the "self" link
            employee = data["items"][0]
            empsUniqID = employee.get("links", [])[0].get("href").split('/')[-1] if employee.get("links") else None
            return empsUniqID
    return None

# Function to fetch all employee details using empsUniqID
def get_employee_details(empsUniqID):
    api_url = f"{ORACLE_HCM_BASE_URL}/emps/{empsUniqID}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the GET request to fetch the employee data
    response = requests.get(api_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    # Check the response status
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch employee details. Status code: {response.status_code}", "details": response.text}

# API endpoint to view employee details using person number
@app.route('/api/view_employee', methods=['POST'])
def view_employee_details():
    # Get the JSON data from the request
    data = request.json
    person_number = data.get('person_number')

    if not person_number:
        return jsonify({"error": "person_number is required"}), 400

    # Step 1: Get empsUniqID using person_number
    empsUniqID = get_employee_unique_id(person_number)
    if not empsUniqID:
        return jsonify({"error": "No employee found for the provided person_number"}), 404

    # Step 2: Fetch all employee details using the empsUniqID
    employee_details = get_employee_details(empsUniqID)

    return jsonify(employee_details)

if __name__ == '__main__':
    app.run(debug=True)
